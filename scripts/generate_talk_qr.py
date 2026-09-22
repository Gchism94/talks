"""Emit the static talk QR SVG. Uses ReportLab; no network or tracking service."""
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

TARGET = "https://gchism94.github.io/talks/design-what-you-know/"
qr = QRCode(None, QRErrorCorrectLevel.M)
qr.addData(TARGET)
qr.make()
border = 4
count = qr.getModuleCount()
size = count + border * 2
paths = []
for y in range(count):
    x = 0
    while x < count:
        start = x
        while x < count and qr.isDark(y, x):
            x += 1
        if x > start:
            paths.append(f"M{start+border} {y+border}h{x-start}v1H{start+border}z")
        else:
            x += 1
print(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" shape-rendering="crispEdges"><title>Open Design What You Know</title><desc>{TARGET}</desc><rect width="{size}" height="{size}" fill="white"/><path d="{"".join(paths)}" fill="black"/></svg>')
