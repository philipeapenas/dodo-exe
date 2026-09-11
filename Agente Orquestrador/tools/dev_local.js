#!/usr/bin/env node
// ═══════════════════════════════════════════════════════
//  dev_local.js - sobe o projeto da pasta atual em localhost.
//
//  PADRAO DO WORKSPACE (30/08/2026): todo projeto responde a `npm run dev`,
//  qualquer que seja a stack por baixo. O fundador nao deve precisar lembrar
//  se aquele projeto e Vercel, Vite, estatico ou Python - ele digita sempre a
//  mesma coisa.
//
//  Este lancador cobre os dois casos que nao tem dev server proprio:
//
//    1. projeto com pasta api/  -> chama a CLI da Vercel, que serve os
//       arquivos E roda as funcoes, igual a producao.
//    2. so arquivo estatico     -> servidor embutido aqui, sem instalar nada.
//
//  Projeto com framework (Next, Vite) NAO usa este arquivo: o `dev` dele ja
//  chama o dev server do proprio framework.
//
//  POR QUE A CLI DA VERCEL E CHAMADA PELO ARQUIVO .js, E NAO POR `vercel dev`:
//  o `vercel dev` le o script `dev` do package.json pra descobrir o comando de
//  desenvolvimento. Se esse script for `vercel dev`, ele detecta que ia chamar
//  a si mesmo e ABORTA com "must not recursively invoke itself" - nada sobe.
//  Chamando o vc.js direto, a recursao nao acontece. Medido em 30/08/2026.
//
//  Uso:
//    node dev_local.js                 -> serve a pasta atual na porta 3000
//    node dev_local.js site            -> serve a subpasta site/
//    node dev_local.js --porta 4000    -> troca a porta
// ═══════════════════════════════════════════════════════

const fs = require('fs');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');

// ── argumentos ─────────────────────────────────────────
const argv = process.argv.slice(2);
let porta = 3000;
let subpasta = '';
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--porta' || argv[i] === '--port') porta = Number(argv[++i]) || porta;
  else if (!argv[i].startsWith('--')) subpasta = argv[i];
}

const projeto = process.cwd();
const raiz = path.resolve(projeto, subpasta);

if (!fs.existsSync(raiz)) {
  console.error(`\nA pasta "${raiz}" nao existe. Confira o caminho no script dev.\n`);
  process.exit(1);
}

// ── 1. Projeto com funcoes: quem serve e a Vercel ──────
// So a CLI dela sabe rodar as funcoes de api/ do mesmo jeito que a producao.
// Sem isso, o site abriria e o catalogo viria vazio - o defeito e silencioso e
// parece bug novo.
const temFuncoes = fs.existsSync(path.join(projeto, 'api'));

function acharVercelCli() {
  const candidatos = [
    path.join(projeto, 'node_modules', 'vercel', 'dist', 'vc.js'),
    process.env.APPDATA && path.join(process.env.APPDATA, 'npm', 'node_modules', 'vercel', 'dist', 'vc.js'),
    '/usr/local/lib/node_modules/vercel/dist/vc.js',
    '/usr/lib/node_modules/vercel/dist/vc.js',
  ].filter(Boolean);
  return candidatos.find((c) => fs.existsSync(c)) || null;
}

if (temFuncoes) {
  const cli = acharVercelCli();
  if (!cli) {
    console.error('\nEste projeto tem pasta api/, entao precisa da CLI da Vercel pra rodar as funcoes.');
    console.error('Instale uma vez com:  npm i -g vercel\n');
    process.exit(1);
  }
  console.log(`\nProjeto com funcoes em api/. Subindo pela Vercel na porta ${porta}...\n`);
  const filho = spawn(process.execPath, [cli, 'dev', '--listen', String(porta)], {
    cwd: projeto,
    stdio: 'inherit',
  });
  filho.on('exit', (codigo) => process.exit(codigo === null ? 1 : codigo));
  return;
}

// ── 2. Site estatico: servidor embutido ────────────────
const TIPOS = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.mp4': 'video/mp4',
  '.webm': 'video/webm',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.txt': 'text/plain; charset=utf-8',
  '.webmanifest': 'application/manifest+json',
};

const servidor = http.createServer((req, res) => {
  let caminho;
  try {
    caminho = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  } catch (_) {
    res.writeHead(400).end('Endereco invalido');
    return;
  }

  // Trava de seguranca: nada fora da pasta servida, mesmo com ../ no endereco.
  const alvo = path.resolve(raiz, '.' + caminho);
  if (alvo !== raiz && !alvo.startsWith(raiz + path.sep)) {
    res.writeHead(403).end('Fora da pasta do projeto');
    return;
  }

  let arquivo = alvo;
  if (fs.existsSync(arquivo) && fs.statSync(arquivo).isDirectory()) {
    // Pasta SEM barra no fim precisa redirecionar antes de servir o index.
    // Sem isso, /admin abre o HTML mas resolve ../css a partir da raiz, e a
    // pagina aparece sem estilo e sem script - defeito ja pago neste
    // workspace, e que parece erro de CSS quando na verdade e de endereco.
    if (!caminho.endsWith('/')) {
      res.writeHead(301, { Location: caminho + '/' }).end();
      return;
    }
    arquivo = path.join(arquivo, 'index.html');
  }

  // Endereco sem extensao tenta o .html correspondente, como a Vercel faz.
  if (!fs.existsSync(arquivo) && !path.extname(arquivo) && fs.existsSync(arquivo + '.html')) {
    arquivo += '.html';
  }

  if (!fs.existsSync(arquivo) || fs.statSync(arquivo).isDirectory()) {
    res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`<h1>404</h1><p>Nao achei <code>${caminho}</code> em <code>${raiz}</code>.</p>`);
    return;
  }

  res.writeHead(200, {
    'Content-Type': TIPOS[path.extname(arquivo).toLowerCase()] || 'application/octet-stream',
    // Local e pra ver mudanca na hora: cache aqui so gera "mas eu ja salvei".
    'Cache-Control': 'no-store',
  });
  fs.createReadStream(arquivo).pipe(res);
});

servidor.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.error(`\nA porta ${porta} ja esta ocupada. Feche o outro servidor,`);
    console.error(`ou suba este em outra porta:  npm run dev -- --porta ${porta + 1}\n`);
    process.exit(1);
  }
  throw e;
});

servidor.listen(porta, () => {
  console.log(`\n  Site no ar:  http://localhost:${porta}`);
  console.log(`  Servindo:    ${raiz}`);
  console.log('\n  Ctrl+C pra parar.\n');
});
