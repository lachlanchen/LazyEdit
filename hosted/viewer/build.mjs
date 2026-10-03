import { build } from 'esbuild';
import { readFileSync } from 'node:fs';
// Bound noVNC's captured fallback cursor, without trapping the system pointer.
await build({entryPoints:['viewer.js'],bundle:true,minify:true,format:'esm',outfile:'/viewer.js',legalComments:'inline',plugins:[{
  name:'bounded-cursor',setup(b){b.onLoad({filter:/\/core\/util\/cursor\.js$/},({path})=>{
    const source=readFileSync(path,'utf8'), marker='    _updatePosition() {';
    if(!source.includes(marker))throw Error('noVNC cursor changed; review the clipping adapter');
    return {loader:'js',contents:source.replace(marker,marker+`
        const desktop = document.getElementById('desktop');
        if (desktop) {
            const rect = desktop.getBoundingClientRect(), x = this._position.x, y = this._position.y;
            this._canvas.style.clipPath = 'inset(' + Math.max(0, rect.top-y) + 'px ' + Math.max(0, x+this._canvas.width-rect.right) + 'px ' + Math.max(0, y+this._canvas.height-rect.bottom) + 'px ' + Math.max(0, rect.left-x) + 'px)';
        }
    `)};
  });}
}]});
