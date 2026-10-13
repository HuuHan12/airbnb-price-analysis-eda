import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile('reports/deliverables/HUY_Bao_cao_ban_giao.docx') as z:
    root = ET.fromstring(z.read('word/document.xml'))
    body = root.find('w:body', NS)
    
    for idx in [16, 17, 19, 20, 25, 27, 65, 66]:
        elem = body[idx]
        tag = elem.tag.split('}')[-1]
        print(f"=== ELEM {idx} ({tag}) ===")
        print(ET.tostring(elem, encoding='unicode')[:500])
        print("...")
