"""Local document exports from a privacy-filtered snapshot."""
from pathlib import Path
from xml.sax.saxutils import escape
import os
from .privacy import protect_report

FILES = ('report.docx', 'records.xlsx', 'report.pdf', 'overview.png', 'overview.jpg', 'overview.webp', 'overview.svg')
NOTE = '本地明细与官方账号统计分别展示，不相加。缺失值为未知。敏感原文请自行查看本地源文件。'

def summary(data):
    local = data.get('totals') or {}
    official = data.get('official_usage') or {}
    rows = [('生成时间', data.get('generated_at')), ('本地总 Token', local.get('total_tokens')),
            ('本地输入 Token', local.get('input_tokens')), ('本地输出 Token', local.get('output_tokens')),
            ('官方同步状态', official.get('status')),
            ('官方累计 Token', (official.get('summary') or {}).get('lifetimeTokens'))]
    if local.get('turn_count') == 0:
        rows=[(k,None if k.startswith('本地') else v) for k,v in rows]
    return [(k, '未知' if v is None else str(v)) for k,v in rows]

def write_exports(report, output):
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from PIL import Image, ImageDraw, ImageFont
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    data = protect_report(report)
    output = Path(output)
    rows = summary(data)
    font_path=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/'msyh.ttc'
    if not font_path.is_file(): raise RuntimeError('local Chinese font required')
    daily = (data.get('official_usage') or {}).get('daily') or []
    def value(row,key):
        v=row.get(key)
        return '未知' if v is None else str(v)
    sections=[('本地每日汇总', ['日期','输入','输出','总 Token'],
               [[value(r,k) for k in ('date','input_tokens','output_tokens','total_tokens')] for r in data.get('daily',[])]),
              ('模型与推理强度', ['模型','推理强度','总 Token'],
               [[value(r,k) for k in ('model','reasoning_effort','total_tokens')] for r in data.get('models',[])]),
              ('官方额度窗口', ['额度池','窗口','已用百分比','重置时间戳'],
               [[value(r,'label'),key,value(r.get(key) or {},'usedPercent'),value(r.get(key) or {},'resetsAt')]
                for r in (data.get('official_usage') or {}).get('rate_limits') or [] for key in ('primary','secondary')])]
    doc = Document()
    for border in doc.styles['Title'].element.xpath('./w:pPr/w:pBdr'):
        border.getparent().remove(border)
    doc.core_properties.author = ''; doc.core_properties.last_modified_by = ''
    style = doc.styles['Normal']; style.font.name = 'Microsoft YaHei'; style.font.size = Pt(10)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    title = doc.add_heading('Codex 用量报告', 0)
    for run in title.runs: run.font.color.rgb = RGBColor(0,0,0)
    doc.add_paragraph(NOTE)
    table = doc.add_table(rows=0, cols=2); table.style = 'Light Shading Accent 1'
    for key,value in rows:
        cells = table.add_row().cells; cells[0].text=key; cells[1].text=value
    doc.add_heading('官方每日用量', 1)
    if not daily: doc.add_paragraph('未提供每日记录；不能据此认为累计用量为零。')
    else:
        table = doc.add_table(rows=1, cols=2); table.style='Light Shading Accent 1'
        table.rows[0].cells[0].text='日期'; table.rows[0].cells[1].text='Token'
        table.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        for row in daily:
            cells=table.add_row().cells; cells[0].text=str(row.get('date','')); cells[1].text=str(row['tokens']) if row.get('tokens') is not None else '未知'
    doc.add_heading('明细与核对', 1)
    doc.add_paragraph('完整匿名记录见同批次 Excel 和 HTML。图片展示概览，所有文件使用同一采集时间。')
    doc.add_paragraph(data['privacy']['note'])
    doc.add_paragraph('额度为采样时快照，超过重置时间后当前剩余额度未知。')
    for heading,headers,records in sections:
        doc.add_heading(heading,1)
        if not records: doc.add_paragraph('未提供记录。'); continue
        table=doc.add_table(rows=1,cols=len(headers)); table.style='Light Shading Accent 1'
        table.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        for cell,text in zip(table.rows[0].cells,headers): cell.text=text
        for record in records:
            for cell,text in zip(table.add_row().cells,record): cell.text=text
    doc.save(output/'report.docx')
    wb=Workbook(); ws=wb.active; ws.title='概览'; ws.append(['项目','值'])
    for row in rows: ws.append(row)
    ws.append(['说明',NOTE])
    flat=wb.create_sheet('全部字段'); flat.append(['字段路径','值'])
    def walk(value, path=''):
        if isinstance(value,dict):
            if not value: flat.append([path,'{}'])
            for key,item in value.items(): walk(item, path+'.'+key if path else key)
        elif isinstance(value,list):
            if not value: flat.append([path,'[]'])
            for i,item in enumerate(value): walk(item,f'{path}[{i}]')
        else: flat.append([path,'未知' if value is None else value])
    walk(data)
    for name,key in [('轮次','turns'),('会话','sessions'),('本地每日','daily'),('官方每日',None)]:
        items=data.get(key,[]) if key else daily
        sheet=wb.create_sheet(name)
        keys=list(dict.fromkeys(k for item in items for k in item if not isinstance(item[k],(dict,list))))
        sheet.append(keys or ['无记录'])
        for item in items: sheet.append(['未知' if item.get(k) is None else item[k] for k in keys])
    for sheet in wb:
        sheet.freeze_panes='A2'; sheet.auto_filter.ref=sheet.dimensions
        sheet.page_setup.orientation='landscape'
        sheet.page_setup.fitToWidth=1; sheet.page_setup.fitToHeight=0
        sheet.sheet_properties.pageSetUpPr.fitToPage=True
        sheet.print_title_rows='1:1'
        for cell in sheet[1]: cell.font=Font(bold=True,color='FFFFFF'); cell.fill=PatternFill('solid',fgColor='233D59')
        for row in sheet:
            for cell in row:
                if isinstance(cell.value,str): cell.data_type='s'
                cell.alignment=Alignment(vertical='top',wrap_text=True)
        for column in sheet.columns: sheet.column_dimensions[column[0].column_letter].width=min(65,max(22,len(str(column[0].value))+3))
        if sheet.title in ('概览','全部字段'):
            sheet.column_dimensions['A'].width=60; sheet.column_dimensions['B'].width=85
        for row in sheet:
            height=max((len(str(c.value or ''))/sheet.column_dimensions[c.column_letter].width for c in row),default=1)
            sheet.row_dimensions[row[0].row].height=min(400,max(22,int(height*30)+15))
        sheet.row_dimensions[1].height=30
    wb.save(output/'records.xlsx')
    pdfmetrics.registerFont(TTFont('ReportChinese',str(font_path),subfontIndex=0))
    pdf=canvas.Canvas(str(output/'report.pdf'),pagesize=(595,842)); pdf.setTitle('Codex 用量报告'); pdf.setAuthor('')
    y=790
    def line(text,size=12):
        nonlocal y
        chunk=max(1,int(490/size))
        for start in range(0,len(text),chunk):
            if y<55: pdf.showPage(); y=790
            pdf.setFont('ReportChinese',size); pdf.drawString(50,y,text[start:start+chunk]); y-=size+9
    line('Codex 用量报告',22); line(NOTE,10)
    for key,value in rows: line(key+'  '+value)
    line('官方每日用量',16)
    for row in daily: line(str(row.get('date',''))+'    '+('未知' if row.get('tokens') is None else str(row['tokens'])))
    if not daily: line('未提供每日记录，不代表零用量。')
    for heading,headers,records in sections:
        line(heading,16); line(' / '.join(headers),10)
        for record in records: line(' / '.join(record),10)
        if not records: line('未提供记录。',10)
    line('额度为采样时快照，超过重置时间后当前剩余额度未知。',10)
    line('完整匿名明细见同批次 Excel 和 HTML。',10); line(data['privacy']['note'],10); pdf.save()
    font_path=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/'msyh.ttc'
    if not font_path.is_file(): raise RuntimeError('local Chinese font required')
    image=Image.new('RGB',(1400,980),'#F3F6FA'); draw=ImageDraw.Draw(image)
    font=ImageFont.truetype(str(font_path),28); heading=ImageFont.truetype(str(font_path),46)
    draw.text((70,50),'Codex 用量概览',font=heading,fill='#233D59')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="980"><rect width="1400" height="980" fill="#F3F6FA"/><g font-family="Microsoft YaHei,sans-serif" fill="#233D59"><text x="70" y="95" font-size="46">Codex 用量概览</text>']
    for i,(key,value) in enumerate(rows):
        y=155+i*95
        draw.text((70,y),key,font=font,fill='#53677B'); draw.text((600,y),value[:45],font=font,fill='#162B41')
        svg.append(f'<text x="70" y="{y+30}" font-size="28">{escape(key)}</text><text x="600" y="{y+30}" font-size="28">{escape(value)}</text>')
    notes=['本地与官方口径不同，不能相加；未知不等于零。','图片仅展示概览；详细数据见同批次 Excel 与网页。','敏感原文仅提供本地查看指引，报告仅供本机使用。']
    for i,note in enumerate(notes):
        draw.text((70,790+i*48),note,font=font,fill='#53677B')
        svg.append(f'<text x="70" y="{820+i*48}" font-size="28">{escape(note)}</text>')
    for ext,fmt in [('png','PNG'),('jpg','JPEG'),('webp','WEBP')]: image.save(output/('overview.'+ext),fmt)
    (output/'overview.svg').write_text(''.join(svg)+'</g></svg>',encoding='utf-8')
