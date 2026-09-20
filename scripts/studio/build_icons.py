#!/usr/bin/env python
"""Rasterize the existing repository SVG logo into native/PWA icon sizes."""
import pathlib,subprocess,tempfile
r=pathlib.Path(__file__).resolve().parents[2]
svg=(r/'figs/logo.svg').read_text();nested=svg[svg.index('>')+1:svg.rindex('</svg>')]
source=f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1320 1320"><rect width="1320" height="1320" fill="white"/><g transform="translate(0 137.5)">{nested}</g></svg>'
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'icon.svg';p.write_text(source)
 for dest,size in [(r/'studio/web/icon.png',1024),(r/'mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png',1024)]+[(r/f'mobile/android/app/src/main/res/mipmap-{density}/{name}.png',size) for density,size in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)] for name in ['ic_launcher','ic_launcher_round']]:
  dest.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['convert','-background','white',str(p),'-resize',f'{size}x{size}',str(dest)],check=True)
# Use the same raster icon for adaptive foreground to preserve brand, no default Capacitor icon.
for density,size in [('mdpi',108),('hdpi',162),('xhdpi',216),('xxhdpi',324),('xxxhdpi',432)]:
 subprocess.run(['convert',str(r/'studio/web/icon.png'),'-resize',f'{size}x{size}',str(r/f'mobile/android/app/src/main/res/mipmap-{density}/ic_launcher_foreground.png')],check=True)
