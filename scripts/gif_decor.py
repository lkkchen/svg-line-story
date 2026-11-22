"""Optional transparent GIF decoration layers for SVG Story Director.

The line, motifs, typography and core animation remain editable SVG/SMIL. GIFs are
small, locally sourced embellishments. Browser playback is started with a fresh
Blob URL at the path-arrival cue; a no-JS export only gates their visibility and
cannot promise GIF decode begins at the cue.

GIF metadata parsing and compiling require Python's standard library only.
"""
from __future__ import annotations

import base64
from pathlib import Path, PurePosixPath

MAX_GIF_BYTES = 2_000_000
MAX_GIF_DIM = 800
MAX_DECORS = 15


def _subblocks(data: bytes, pos: int):
    """Return GIF data sub-block payload and next index; fail on truncated GIF."""
    blocks = []
    while True:
        if pos >= len(data):
            raise ValueError('GIF sub-block truncated')
        size = data[pos]
        pos += 1
        if not size:
            return b''.join(blocks), pos
        if pos + size > len(data):
            raise ValueError('GIF sub-block overflows file')
        blocks.append(data[pos:pos + size])
        pos += size


def gif_info(data: bytes):
    """Read dimensions, frame count, duration, loop extension and transparency."""
    if len(data) < 14 or data[:6] not in (b'GIF87a', b'GIF89a'):
        raise ValueError('Asset is not a GIF87a/GIF89a image')
    width = int.from_bytes(data[6:8], 'little')
    height = int.from_bytes(data[8:10], 'little')
    if not (1 <= width <= MAX_GIF_DIM and 1 <= height <= MAX_GIF_DIM):
        raise ValueError(f'GIF dimensions out of allowed range: {width}x{height}')
    packed = data[10]
    pos = 13
    if packed & 0x80:
        pos += 3 * (2 ** ((packed & 7) + 1))
    if pos >= len(data):
        raise ValueError('GIF global color table truncated')
    frames = 0
    delay_cs = 10
    duration_ms = 0
    has_transparency = False
    loop_count = None  # absence of NETSCAPE extension = one play
    ended = False
    while pos < len(data):
        block = data[pos]
        pos += 1
        if block == 0x3B:
            ended = True
            break
        if block == 0x21:  # extension
            if pos >= len(data):
                raise ValueError('GIF extension truncated')
            label = data[pos]
            pos += 1
            if label == 0xF9:  # Graphic Control Extension
                if pos + 6 > len(data) or data[pos] != 4 or data[pos + 5] != 0:
                    raise ValueError('GIF graphic control extension invalid')
                flags = data[pos + 1]
                delay_cs = int.from_bytes(data[pos + 2:pos + 4], 'little')
                if flags & 1:
                    has_transparency = True
                pos += 6
            elif label == 0xFF:  # Application Extension
                if pos >= len(data):
                    raise ValueError('GIF application extension truncated')
                size = data[pos]
                pos += 1
                if pos + size > len(data):
                    raise ValueError('GIF application identifier truncated')
                app = data[pos:pos + size]
                pos += size
                payload, pos = _subblocks(data, pos)
                if app in (b'NETSCAPE2.0', b'ANIMEXTS1.0') and len(payload) >= 3 and payload[0] == 1:
                    loop_count = int.from_bytes(payload[1:3], 'little')
            else:
                if pos >= len(data):
                    raise ValueError('GIF extension data truncated')
                size = data[pos]
                pos += 1
                pos += size
                if pos > len(data):
                    raise ValueError('GIF extension payload truncated')
                _, pos = _subblocks(data, pos)
        elif block == 0x2C:  # Image Descriptor
            if pos + 9 > len(data):
                raise ValueError('GIF image descriptor truncated')
            image_packed = data[pos + 8]
            pos += 9
            if image_packed & 0x80:
                pos += 3 * (2 ** ((image_packed & 7) + 1))
            if pos >= len(data):
                raise ValueError('GIF local color table truncated')
            pos += 1  # LZW min code size
            _, pos = _subblocks(data, pos)
            frames += 1
            # Browsers often clamp tiny GIF frame durations. Use 20ms minimum.
            duration_ms += max(20, delay_cs * 10)
            delay_cs = 10
        else:
            raise ValueError(f'Invalid GIF block at offset {pos - 1}: {block:#x}')
    if not ended or frames < 2:
        raise ValueError('Expected a complete animated GIF with at least 2 frames')
    return {'width': width, 'height': height, 'frames': frames,
            'naturalSeconds': round(duration_ms / 1000, 3),
            'loopCount': loop_count, 'transparent': has_transparency}


def validate_gif_decorations(story, object_ids: set):
    errors = []
    ids = set()
    count = 0
    w = story.get('canvas', {}).get('width', 750)
    h = story.get('canvas', {}).get('height', 4050)
    for chapter in story.get('chapters', []):
        items = chapter.get('gifDecorations', [])
        if not isinstance(items, list):
            errors.append(f'gifDecorations in {chapter.get("id")} must be a list')
            continue
        if len(items) > 3:
            errors.append(f'{chapter.get("id")}: max 3 GIF accents per chapter (avoid a GIF collage)')
        for item in items:
            count += 1
            if not isinstance(item, dict):
                errors.append('GIF decoration must be an object')
                continue
            ident = item.get('id')
            if not isinstance(ident, str) or not ident or not ident.replace('-', '').replace('_', '').isalnum() or not ident[0].isalpha():
                errors.append(f'Invalid GIF decoration id: {ident}')
            if ident in ids or ident in object_ids:
                errors.append(f'Duplicate GIF decoration id: {ident}')
            ids.add(ident)
            try:
                safe_asset_path(item.get('src', ''))
            except (TypeError, ValueError) as e:
                errors.append(f'{ident}: {e}')
            for key in ('width', 'height'):
                val = item.get(key)
                if not isinstance(val, (float, int)) or not 12 <= val <= 360:
                    errors.append(f'{ident}: {key} should be 12–360 design units')
            if 'attachTo' in item:
                if item['attachTo'] not in object_ids:
                    errors.append(f'{ident}: attachTo references missing SVG motif {item["attachTo"]}')
                if not (isinstance(item.get('offset', [0, 0]), list) and len(item.get('offset', [0, 0])) == 2 and
                        all(isinstance(v, (float, int)) for v in item.get('offset', [0, 0]))):
                    errors.append(f'{ident}: offset must be [dx,dy]')
            elif not (isinstance(item.get('x'), (int, float)) and isinstance(item.get('y'), (int, float))):
                errors.append(f'{ident}: set attachTo or numeric x/y coordinates')
            elif abs(item['x']) > w + 300 or not -200 <= item['y'] <= h + 200:
                errors.append(f'{ident}: GIF location far outside canvas')
            cue = item.get('trigger')
            if isinstance(cue, dict) and list(cue) == ['hit']:
                if cue['hit'] not in object_ids:
                    errors.append(f'{ident}: trigger hit references missing SVG motif {cue["hit"]}')
            elif isinstance(cue, (int, float)):
                if not 0 <= cue <= story.get('duration', 0):
                    errors.append(f'{ident}: trigger second out of range')
            else:
                errors.append(f'{ident}: trigger must be seconds or {{"hit":"object-id"}}')
            if item.get('playback', 'once') not in ('once', 'loop'):
                errors.append(f'{ident}: playback must be once or loop')
            if item.get('z', 'front') not in ('back', 'front'):
                errors.append(f'{ident}: z must be back or front')
            for key in ('offsetSeconds', 'fadeInSeconds', 'fadeOutSeconds'):
                if key in item and (not isinstance(item[key], (float, int)) or abs(item[key]) > 5):
                    errors.append(f'{ident}: {key} is invalid')
            if 'activeSeconds' in item and (not isinstance(item['activeSeconds'], (float, int)) or not .2 <= item['activeSeconds'] <= 15):
                errors.append(f'{ident}: activeSeconds must be 0.2–15s')
    if count > MAX_DECORS:
        errors.append(f'Too many GIF decorations: {count} (max {MAX_DECORS})')
    return errors


def safe_asset_path(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '?' in value or '#' in value:
        raise ValueError('src must be a local relative GIF file, not an absolute path, URL or data URI')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or path.suffix.lower() != '.gif':
        raise ValueError('src must be a .gif under the story folder with no ../ segments')
    return path


def load_decorations(story, prepared, source_dir: Path):
    """Resolve cue and bytes. Called by compiler or full-path validator."""
    objects = prepared['objects']
    errors = validate_gif_decorations(story, set(objects))
    if errors:
        raise ValueError('\n'.join(errors))
    arrivals = {}
    for connection in prepared['connections']:
        arrivals.setdefault(connection['object'], connection['lineArrival'])
    resolved = []
    source_dir = source_dir.resolve()
    for ch in story['chapters']:
        for item in ch.get('gifDecorations', []):
            ident = item['id']
            rel = safe_asset_path(item['src'])
            absolute = (source_dir / rel).resolve()
            if not absolute.is_relative_to(source_dir):
                raise ValueError(f'{ident}: symlink escaped story folder')
            if not absolute.is_file():
                raise ValueError(f'{ident}: missing GIF asset {rel}')
            if absolute.stat().st_size > MAX_GIF_BYTES:
                raise ValueError(f'{ident}: GIF too large (limit {MAX_GIF_BYTES} bytes)')
            data = absolute.read_bytes()
            info = gif_info(data)
            if not info['transparent']:
                raise ValueError(f'{ident}: decorative GIF must have transparency')
            playback = item.get('playback', 'once')
            if playback == 'once' and info['loopCount'] is not None:
                raise ValueError(f'{ident}: once GIF must have no looping extension (found {info["loopCount"]})')
            if playback == 'loop' and info['loopCount'] != 0:
                raise ValueError(f'{ident}: looping GIF must have a NETSCAPE infinite-loop extension')
            if playback == 'loop' and 'activeSeconds' not in item:
                raise ValueError(f'{ident}: loop GIF requires activeSeconds')
            cue_spec = item['trigger']
            if isinstance(cue_spec, dict):
                if cue_spec['hit'] not in arrivals:
                    raise ValueError(f'{ident}: trigger object {cue_spec["hit"]} is not on main path')
                cue = arrivals[cue_spec['hit']]
            else:
                cue = float(cue_spec)
            cue += float(item.get('offsetSeconds', 0))
            if cue < 0:
                raise ValueError(f'{ident}: cue before story starts')
            length = float(item.get('activeSeconds', info['naturalSeconds']))
            if cue + length > story['duration'] + 0.01:
                raise ValueError(f'{ident}: GIF decoration continues beyond story duration')
            fade_in = max(0., float(item.get('fadeInSeconds', .12)))
            fade_out = max(0., float(item.get('fadeOutSeconds', .24)))
            if fade_in + fade_out >= length:
                raise ValueError(f'{ident}: total fade duration is longer than activeSeconds')
            if 'attachTo' in item:
                anchor = objects[item['attachTo']]['anchor']
                offset = item.get('offset', [0, 0])
                x, y = (anchor[0] + offset[0], anchor[1] + offset[1])
            else:
                x, y = float(item['x']), float(item['y'])
            if x + item['width'] < 0 or y + item['height'] < 0 or x > story['canvas']['width'] or y > story['canvas']['height']:
                raise ValueError(f'{ident}: decorative GIF entirely outside story canvas')
            resolved.append({**item, 'id': ident, 'x': float(x), 'y': float(y),
                             'begin': round(cue, 3), 'end': round(cue + length, 3),
                             'duration': round(length, 3), 'naturalDuration': info['naturalSeconds'],
                             'fadeIn': fade_in, 'fadeOut': fade_out,
                             'playback': playback, 'z': item.get('z', 'front'),
                             'src': rel.as_posix(), 'bytes': data,
                             'base64': base64.b64encode(data).decode('ascii'), 'gifInfo': info})
    return resolved
