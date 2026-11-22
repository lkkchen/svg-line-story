"""Tiny hand-authored, fully inline SVG motif library inspired by the V1 line-art language.
All motifs use a 200x200 local design box and declare an interaction pin at (100,180).
No bitmap, font file, external dependency or JS is used in this module.

Fills follow the active palette. The original spring hex values are kept only
when the story still uses that exact set, so older spring scrolls do not shift.
"""
from html import escape
from palettes import is_spring_colors, mix, rel_luminance

MOTIFS = (
    "pencil", "sprout", "flower", "boat", "cloud", "sun", "hill", "butterfly",
    "bird", "tree", "moon", "star", "book", "kite", "lighthouse", "shell",
    "gift", "balloon", "house", "rocket", "lantern", "heart", "leaf", "wave"
)

# Visual contact pins in each 200x200 motif. For new motifs use customMotifs.anchorLocal.
MOTIF_ANCHORS = {
  'pencil': (100,180), 'sprout': (100,180), 'flower': (100,180), 'boat': (100,180),
  'cloud': (100,131), 'sun': (100,190), 'hill': (100,154), 'butterfly': (100,120),
  'bird': (102,139), 'tree': (100,180), 'moon': (95,173), 'star': (48,182),
  'book': (100,181), 'kite': (100,180), 'lighthouse': (100,180), 'shell': (100,165),
  'gift': (100,181), 'balloon': (100,180), 'house': (100,179), 'rocket': (100,180),
  'lantern': (100,180), 'heart': (100,171), 'leaf': (100,181), 'wave': (100,171)
}

# Built-in SMIL family. draw = stroke reveals, pop = scale with a small overshoot,
# sway = one settle rotation or flap, still = no transform. Adjacent chapter heroes
# should not share a family. A custom motif defaults to still until story.json sets motion.
MOTIF_MOTION = {
    'pencil': 'still', 'sprout': 'draw', 'flower': 'pop', 'boat': 'sway',
    'cloud': 'still', 'sun': 'still', 'hill': 'still', 'butterfly': 'sway',
    'bird': 'still', 'tree': 'still', 'moon': 'still', 'star': 'still',
    'book': 'still', 'kite': 'still', 'lighthouse': 'still', 'shell': 'still',
    'gift': 'still', 'balloon': 'still', 'house': 'still', 'rocket': 'still',
    'lantern': 'still', 'heart': 'still', 'leaf': 'still', 'wave': 'still',
}

# Authored spring materials. Keys match materials().
SPRING_MATERIALS = {
    'wood': '#E9B776', 'woodHi': '#F6DBC1', 'nib': '#F9E2C8', 'lead': '#FCDEAB',
    'soil': '#C99567', 'leaf2': '#C3D6AF', 'leaf3': '#CBDBB7',
    'petal0': '#F0C5B6', 'petal1': '#F5D8BB', 'petal2': '#EECAC4',
    'petal3': '#F0BFAE', 'petal4': '#F2D8CB', 'petal5': '#F4CCBC',
    'hull': '#FBF4E9', 'sail': '#EFC9A8', 'sail2': '#DFB69B',
    'sun': '#F4DDA9', 'hill2': '#CDDCC9',
    'wingL': '#F3CBBB', 'wingR': '#F5D4A6',
    'bird': '#FDF9EE', 'canopy': '#C4D9BD', 'moon': '#F5DEA8', 'star': '#F4DBA6',
    'book': '#F9E6C8', 'kite': '#E7D6C5', 'kiteTail': '#D9E5D3',
    'tower': '#FAECD6', 'towerCap': '#F4CBA8', 'shell': '#F5D7BD',
    'gift': '#F7DBC4', 'giftBow': '#F4C28D',
    'balloon': '#F2C9B7', 'shine': '#FFF6EE', 'shine2': '#FCF0E2',
    'house': '#F6E6CF', 'window': '#CEE0D5',
    'rocket': '#F8E9CF', 'fin': '#D3E4D8', 'lantern': '#F5D4AF',
    'heart': '#EFBEB9', 'leaf': '#C6DAC3',
}


def materials(palette):
    if is_spring_colors(palette):
        return dict(SPRING_MATERIALS)
    paper = palette.get('paper', '#FCFAF4')
    ink, sage, orange = palette['ink'], palette['sage'], palette['orange']
    rose, light, sky = palette['rose'], palette['light'], palette['sky']
    dark = rel_luminance(paper) < 0.4
    shine = mix(ink, paper, 0.78) if dark else mix(paper, '#FFFFFF', 0.72)
    shine2 = mix(ink, paper, 0.62) if dark else mix(paper, rose, 0.16)
    return {
        'wood': mix(orange, ink, 0.22),
        'woodHi': mix(orange, paper, 0.5),
        'nib': mix(rose, paper, 0.42),
        'lead': mix(orange, paper, 0.62),
        'soil': mix(orange, ink, 0.4),
        'leaf2': mix(sage, light, 0.38),
        'leaf3': mix(sage, light, 0.48),
        'petal0': rose,
        'petal1': mix(rose, orange, 0.38),
        'petal2': mix(rose, paper, 0.22),
        'petal3': mix(orange, rose, 0.28),
        'petal4': mix(rose, light, 0.35),
        'petal5': mix(rose, orange, 0.16),
        'hull': mix(paper, rose, 0.16),
        'sail': mix(orange, rose, 0.42),
        'sail2': mix(orange, ink, 0.16),
        'sun': mix(orange, paper, 0.48),
        'hill2': mix(sage, light, 0.5),
        'wingL': mix(rose, paper, 0.12),
        'wingR': mix(orange, paper, 0.32),
        'bird': mix(paper, light, 0.35),
        'canopy': mix(sage, light, 0.28),
        'moon': mix(orange, paper, 0.5),
        'star': mix(orange, paper, 0.46),
        'book': mix(rose, paper, 0.4),
        'kite': mix(rose, light, 0.32),
        'kiteTail': mix(sage, light, 0.45),
        'tower': mix(rose, paper, 0.45),
        'towerCap': mix(orange, rose, 0.32),
        'shell': mix(rose, orange, 0.32),
        'gift': mix(rose, paper, 0.36),
        'giftBow': mix(orange, paper, 0.26),
        'balloon': mix(rose, orange, 0.28),
        'shine': shine,
        'shine2': shine2,
        'house': mix(rose, paper, 0.4),
        'window': mix(sage, sky, 0.45),
        'rocket': mix(rose, paper, 0.48),
        'fin': mix(sage, sky, 0.4),
        'lantern': mix(orange, rose, 0.38),
        'heart': mix(rose, orange, 0.2),
        'leaf': mix(sage, light, 0.25),
    }


def motif_markup(name, palette, begin=0.0):
    ink=escape(palette['ink']); sage=escape(palette['sage']); orange=escape(palette['orange'])
    rose=escape(palette['rose']); light=escape(palette['light']); sky=escape(palette['sky'])
    m=materials(palette)
    b=f'{float(begin):.2f}s'
    base=''
    if name=='pencil':
        base=f'''<path d="M44 26 Q50 15 60 18 L128 136 103 167 33 45 Q28 34 44 26Z" fill="{m['wood']}" stroke-width="3.3"/>
         <path d="M44 26L33 45 58 33 60 18Z" fill="{m['woodHi']}" stroke-width="2.2"/>
         <path d="M103 167L100 180 128 136Z" fill="{m['nib']}" stroke-width="3.3"/>
         <path d="M99 174L100 180 108 174Z" fill="{ink}" stroke-width="1"/>
         <path d="M49 42L111 149" stroke="{m['lead']}" stroke-width="4"/>
         <circle cx="156" cy="64" r="5" fill="{orange}" stroke="none"/>'''
    elif name=='sprout':
        base=f'''<path d="M72 181Q102 190 130 182" fill="none" stroke="{sage}" stroke-width="2.1" stroke-dasharray="4 8"/>
         <path d="M91 168Q111 151 120 171Q115 185 100 181Q83 178 91 168Z" fill="{m['soil']}" stroke-width="2.7"/>
         <path d="M100 177Q93 135 106 77" fill="none" stroke-width="4.3" stroke-dasharray="112" stroke-dashoffset="112">
           <animate attributeName="stroke-dashoffset" from="112" to="0" begin="{b}" dur="2.2s" fill="freeze" restart="never"/></path>
         <g transform="translate(100 120)"><g><path d="M0 0Q-66 -13 -65 -58Q-12 -53 0 0Z" fill="{sage}" stroke-width="2.7"/><path d="M-2 -2Q-31 -38 -56 -52" stroke="{ink}" stroke-width="1.4" fill="none"/>
         <animateTransform attributeName="transform" type="scale" values="0.03;1.06;1" keyTimes="0;.8;1" calcMode="spline" keySplines="0.45 0 0.2 1; 0.25 0 0.35 1" begin="{b}" dur="2.5s" fill="freeze" restart="never"/></g></g>
         <g transform="translate(106 93)"><g><path d="M0 0Q53 -16 54 -48Q13 -47 0 0Z" fill="{m['leaf2']}" stroke-width="2.6"/><path d="M0 0Q27 -31 46 -42" fill="none" stroke-width="1.5"/>
         <animateTransform attributeName="transform" type="scale" values="0.02;1.05;1" keyTimes="0;.8;1" calcMode="spline" keySplines="0.45 0 0.2 1; 0.25 0 0.35 1" begin="{float(begin)+.4:.2f}s" dur="2.2s" fill="freeze" restart="never"/></g></g>
         <circle cx="144" cy="39" r="4" fill="{orange}" stroke="none"/>'''
    elif name=='flower':
        petal_bits=[]
        for i, angle in enumerate(range(0, 360, 60)):
            fill=m['petal'+str(i)]
            petal_bits.append(f'<g transform="rotate({angle})"><path d="M0 -3Q-27 -20 -21 -59Q-6 -88 0 -85Q21 -76 21 -52Q20 -21 0 -3Z" fill="{fill}" stroke-width="2.2"/><path d="M0 -7V-51" fill="none" stroke="{orange}" stroke-width="1.2" opacity=".6"/></g>')
        petals=''.join(petal_bits)
        base=f'''<path d="M100 181C94 149 104 113 100 73" fill="none" stroke-width="4.4"/>
          <path d="M100 156Q45 148 47 120Q85 112 100 156Z" fill="{sage}" stroke-width="2.6"/>
          <path d="M100 139Q156 128 151 105Q121 112 100 139Z" fill="{m['leaf3']}" stroke-width="2.6"/>
          <g transform="translate(100 69)"><g>{petals}<circle r="17" fill="{orange}" stroke-width="2.4"/>
          <circle cx="-5" cy="-4" r="2.3" fill="{ink}" stroke="none"/><circle cx="6" cy="6" r="2" fill="{ink}" stroke="none"/>
          <animateTransform attributeName="transform" type="scale" values="0.06;0.28;1.08;1" keyTimes="0;.21;.85;1" calcMode="spline" keySplines="0.45 0 0.2 1; 0.2 0 0.15 1; 0.3 0 0.4 1" begin="{b}" dur="2.4s" fill="freeze" restart="never"/></g></g>'''
    elif name=='boat':
        base=f'''<path d="M23 180Q100 166 177 179" fill="none" stroke="{sky}" stroke-width="4"/><path d="M45 191Q100 178 156 191" fill="none" stroke="{sky}" stroke-width="2.3"/>
          <g transform="translate(100 138)"><g>
          <path d="M-65 2L68 2 35 36-39 36Z" fill="{m['hull']}" stroke-width="3.5"/>
          <path d="M0 -73L-51 0H0Z" fill="{m['sail']}" stroke-width="2.6"/>
          <path d="M0 -73L54 0H0Z" fill="{m['sail2']}" stroke-width="2.6"/>
          <path d="M-40 7L40 7M-39 36L0 14 35 36" fill="none" stroke-width="2.1"/>
          <animateTransform attributeName="transform" type="rotate" values="-3;3;-2;0" keyTimes="0;0.34;0.67;1" calcMode="spline" keySplines="0.4 0 0.2 1; 0.3 0 0.3 1; 0.2 0 0.25 1" begin="{b}" dur="3.3s" fill="freeze" restart="never"/></g></g>'''
    elif name=='cloud':
        base=f'''<path d="M24 129Q13 101 50 95Q63 48 105 68Q133 37 159 82Q195 77 190 119Q173 143 29 135Z" fill="{sky}" stroke-width="2.7"/><path d="M47 121Q104 133 171 122" fill="none" stroke="{sage}" stroke-width="2" stroke-dasharray="16 9"/>'''
    elif name=='sun':
        rays=''.join(f'<path d="M100 10V27" transform="rotate({ang} 100 100)" stroke="{orange}" fill="none" stroke-width="3"/>' for ang in range(0,360,45))
        sun=m['sun']
        base=f'<circle cx="100" cy="100" r="57" fill="{sun}" stroke-width="3.1"/>{rays}<path d="M79 101q8 7 15 0M106 101q8 7 15 0M86 122q15 12 30 0" fill="none" stroke-width="2.5"/>'
    elif name=='hill':
        base=f'''<path d="M0 116Q50 75 101 115Q158 71 200 111V196H0Z" fill="{light}" stroke="none"/>
          <path d="M0 154Q46 121 96 162Q155 120 200 151V196H0Z" fill="{m['hill2']}" stroke="none"/>
          <path d="M0 154Q46 121 96 162Q155 120 200 151" fill="none" stroke-width="2"/>
          <path d="M45 174v-26m-8 10 8 6 11-14M153 170v-29m-8 12 8 7 9-13" fill="none" stroke-width="2"/>'''
    elif name=='butterfly':
        base=f'''<g transform="translate(100 95)"><g><path d="M-3 -3C-52 -65 -82 -52 -62 -9C-93 31 -39 51 -4 15Z" fill="{m['wingL']}" stroke-width="2.8"/><path d="M3 -3C48 -66 79 -50 63 -9C84 34 33 52 4 15Z" fill="{m['wingR']}" stroke-width="2.8"/><path d="M0 -9v34M-4 -3Q-18 -29 -29 -31M4 -3Q18 -29 29 -31" fill="none" stroke-width="2.4"/>
          <animateTransform attributeName="transform" type="scale" values="1 1;.68 1;1 1" begin="{b}" dur="1.2s" repeatCount="3" fill="freeze"/></g></g>'''
    elif name=='bird':
        base=f'''<path d="M27 114Q70 78 101 111Q130 77 173 113Q132 100 102 139Q66 101 27 114Z" fill="{m['bird']}" stroke-width="3.1"/><path d="M101 111Q100 80 114 74" fill="none" stroke-width="2"/><circle cx="116" cy="91" r="2.5" fill="{ink}" stroke="none"/>'''
    elif name=='tree':
        base=f'''<path d="M100 180V84M100 129L64 105M101 118L136 91" fill="none" stroke-width="6"/>
          <path d="M102 23C50 8 25 43 43 79Q19 114 61 127Q92 150 113 126Q157 139 166 103Q185 69 153 57Q152 27 102 23Z" fill="{m['canopy']}" stroke-width="3.1"/>
          <path d="M72 69Q101 50 119 79M84 108Q114 98 137 89" fill="none" stroke="{sage}" stroke-width="2"/>'''
    elif name=='moon':
        moon=m['moon']
        base=f'<path d="M131 36Q56 57 65 112Q74 170 152 152Q95 193 57 154Q18 103 62 55Q93 24 131 36Z" fill="{moon}" stroke-width="3.1"/><circle cx="169" cy="50" r="4" fill="{orange}" stroke="none"/>'
    elif name=='star':
        base=f'''<path d="M100 22L124 76 181 85 140 124 152 182 100 154 48 182 60 124 19 85 76 76Z" fill="{m['star']}" stroke-width="3.2"/>
          <path d="M80 109Q93 105 101 110M113 109Q124 106 130 110" fill="none" stroke-width="2.1"/><circle cx="100" cy="128" r="2" fill="{ink}" stroke="none"/>'''
    elif name=='book':
        base=f'''<path d="M100 62Q61 43 27 63V170Q70 152 100 177Q129 151 174 168V63Q135 42 100 62Z" fill="{m['book']}" stroke-width="3.1"/>
          <path d="M100 62V177M42 89Q69 76 85 89M42 113Q66 103 85 112M114 91Q144 76 160 90M114 114Q142 106 161 114" fill="none" stroke-width="2.1"/>
          <path d="M24 170Q62 161 100 181Q136 161 176 171" fill="none" stroke="{orange}" stroke-width="2"/>'''
    elif name=='kite':
        base=f'''<path d="M102 24L160 92 101 141 48 90Z" fill="{m['kite']}" stroke-width="3"/>
          <path d="M102 24V141M48 90H160" fill="none" stroke-width="2"/>
          <path d="M101 141Q85 160 104 172L100 180" fill="none" stroke="{orange}" stroke-width="2.6"/>
          <path d="M101 150l-15 -5 4 14 12 -3M101 169l12 -7 4 14 -12 -3" fill="{m['kiteTail']}" stroke-width="1.8"/>'''
    elif name=='lighthouse':
        base=f'''<path d="M78 180L88 68H117L129 180Z" fill="{m['tower']}" stroke-width="3.5"/>
          <path d="M87 105H119M83 145H125" stroke="{orange}" stroke-width="9"/>
          <path d="M81 68H124V52H81ZM73 52L103 31 132 52Z" fill="{m['towerCap']}" stroke-width="3"/>
          <path d="M97 180V149Q104 140 113 149V180" fill="{light}" stroke-width="2.3"/>
          <path d="M52 66L77 74M153 66L126 74" stroke="{orange}" stroke-width="2.4"/>'''
    elif name=='shell':
        base=f'''<path d="M31 165Q10 97 44 63Q78 28 100 75Q133 22 167 72Q189 112 166 165Z" fill="{m['shell']}" stroke-width="3.2"/>
          <path d="M100 76L101 164M73 73Q54 106 70 161M127 70Q148 107 129 161" fill="none" stroke="{orange}" stroke-width="2.4"/>
          <path d="M31 165Q98 154 166 165" fill="none" stroke-width="2.7"/>'''
    elif name=='gift':
        base=f'''<rect x="44" y="92" width="112" height="89" rx="4" fill="{m['gift']}" stroke-width="3.2"/>
          <path d="M35 91H166V75H35ZM94 74V181" fill="{sage}" stroke-width="3"/><path d="M98 76Q42 57 69 41Q88 30 100 75Q120 22 138 40Q159 62 98 76Z" fill="{m['giftBow']}" stroke-width="3"/>'''
    elif name=='balloon':
        base=f'''<path d="M100 148C34 112 62 33 99 28C150 24 159 105 100 148Z" fill="{m['balloon']}" stroke-width="3.1"/>
          <path d="M100 148l-9 9h18Z" fill="{orange}" stroke-width="2"/>
          <path d="M100 157Q113 170 100 180" fill="none" stroke-width="2.6"/>
          <path d="M89 46Q77 59 80 75" fill="none" stroke="{m['shine']}" stroke-width="6"/>'''
    elif name=='house':
        base=f'''<path d="M43 98L100 42 158 98V179H42V98Z" fill="{m['house']}" stroke-width="3.2"/>
          <path d="M30 99L100 28 171 99" fill="none" stroke="{orange}" stroke-width="8"/>
          <path d="M87 179V122H117V179M53 117H76V143H53Z" fill="{m['window']}" stroke-width="3"/>
          <circle cx="108" cy="155" r="2" fill="{orange}" stroke="none"/>'''
    elif name=='rocket':
        base=f'''<path d="M74 129Q65 55 117 27Q154 80 117 145Z" fill="{m['rocket']}" stroke-width="3"/>
          <path d="M76 111L48 131 66 158 86 135M123 126L154 142 129 164 112 139" fill="{m['fin']}" stroke-width="3"/>
          <circle cx="109" cy="87" r="18" fill="{sky}" stroke-width="3"/><path d="M87 151L100 180 116 154" fill="none" stroke="{orange}" stroke-width="6"/>'''
    elif name=='lantern':
        base=f'''<path d="M98 39V59M82 57H116" fill="none" stroke-width="3"/>
          <path d="M57 77Q100 51 143 77V137Q100 164 57 137Z" fill="{m['lantern']}" stroke-width="3.2"/>
          <path d="M58 85H142M58 130H142M100 63V151" fill="none" stroke="{orange}" stroke-width="2.5"/>
          <path d="M99 151V180M90 173L100 180 110 173" fill="none" stroke-width="2.7"/>'''
    elif name=='heart':
        base=f'''<path d="M100 171C64 130 22 108 35 68C53 29 83 46 100 70C124 34 160 34 168 78C179 115 141 139 100 171Z" fill="{m['heart']}" stroke-width="3.5"/>
          <path d="M61 70Q71 56 82 69" fill="none" stroke="{m['shine2']}" stroke-width="6"/>'''
    elif name=='leaf':
        base=f'''<path d="M100 181Q48 132 44 77Q90 21 156 34Q176 132 100 181Z" fill="{m['leaf']}" stroke-width="3.1"/>
          <path d="M100 181Q106 90 151 46M105 141Q84 103 61 89M122 100Q153 104 162 91" fill="none" stroke="{sage}" stroke-width="3"/>'''
    elif name=='wave':
        base=f'''<path d="M13 145Q49 88 82 139Q109 180 143 133Q166 105 188 144" fill="none" stroke="{sky}" stroke-width="12"/>
          <path d="M17 171Q45 155 73 172Q106 187 141 166Q166 153 189 170" fill="none" stroke-width="3"/>'''
    else:
        raise ValueError(f'Unknown motif: {name}. Add a vector motif or use a supported one.')
    # SVG inks share one common outline grammar; individual fills do the storytelling.
    return f'<g stroke="{ink}" stroke-linecap="round" stroke-linejoin="round">{base}</g>'
