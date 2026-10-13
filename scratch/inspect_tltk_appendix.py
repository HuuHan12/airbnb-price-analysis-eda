import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile('reports/deliverables/HUY_Bao_cao_ban_giao.docx') as z:
    root = ET.fromstring(z.read('word/document.xml'))
    body = root.find('w:body', NS)
    for i in range(89, len(body)):
        elem = body[i]
        tag = elem.tag.split('}')[-1]
        if tag == 'p':
            texts = [t.text for t in elem.findall('.//w:t', NS) if t.text]
            full_text = ''.join(texts).strip()
            style = elem.find('.//w:pStyle', NS)
            s_name = style.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if style is not None else 'Normal'
            print(f'P{i:03d} [{s_name}]: {full_text}')
        elif tag == 'tbl':
            rows = elem.findall('.//w:tr', NS)
            print(f'TBL{i:03d}: [Table with {len(rows)} rows]')
            for r_idx, r in enumerate(rows):
                cells = [''.join(e.text for e in c.findall('.//w:t', NS) if e.text).strip() for c in r.findall('w:tc', NS)]
                print(f'   Row {r_idx}: {" | ".join(cells)}')
