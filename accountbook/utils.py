from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import csv
import openpyxl
from io import BytesIO
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def get_paginated_queryset(queryset, request, per_page=10):
    """通用分页处理"""
    page = request.GET.get('page', '1')
    paginator = Paginator(queryset, per_page)
    try:
        paginated_obj = paginator.page(page)
    except PageNotAnInteger:
        paginated_obj = paginator.page(1)
    except EmptyPage:
        paginated_obj = paginator.page(paginator.num_pages)
    return paginated_obj

def export_to_csv(queryset, filename, headers, data_func):
    """通用导出 CSV"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)
    writer.writerow(headers)
    for item in queryset:
        writer.writerow(data_func(item))
    return response

def export_to_excel(queryset, filename, headers, data_func):
    """通用导出 Excel"""
    bio = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(headers)
    for item in queryset:
        sheet.append(data_func(item))
    workbook.save(bio)
    bio.seek(0)
    response = HttpResponse(
        bio.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}.xlsx"'},
    )
    return response

def export_to_pdf(queryset, filename, headers, data_func):
    """通用导出 PDF"""
    bio = BytesIO()
    pdf = canvas.Canvas(bio)
    font_path = os.path.join(settings.STATICFILES_DIRS[0], "fonts", "msyh.ttc")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("msyh", font_path))
        pdf.setFont("msyh", 12)
    
    # 绘制表头
    y = 800
    x_offsets = [100, 200, 300, 400]
    for i, header in enumerate(headers):
        pdf.drawString(x_offsets[i], y, header)

    y -= 20
    for item in queryset:
        row = data_func(item)
        for i, val in enumerate(row):
            pdf.drawString(x_offsets[i], y, str(val))
        y -= 20
        if y < 50:
            pdf.showPage()
            if os.path.exists(font_path):
                pdf.setFont("msyh", 12)
            y = 800

    pdf.showPage()
    pdf.save()
    bio.seek(0)
    return FileResponse(bio, as_attachment=True, filename=f"{filename}.pdf")
