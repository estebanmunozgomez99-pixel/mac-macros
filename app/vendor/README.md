# Bundled third-party files

Shipped with the app so nothing is downloaded at runtime (App Store rule 2.5.2).

- `barcode/` – [barcode-detector](https://github.com/Sec-ant/barcode-detector) 3.2.2 (MIT) and the
  [zxing-wasm](https://github.com/Sec-ant/zxing-wasm) 3.1.3 reader (MIT; ZXing-C++ is Apache-2.0). Used only when
  the browser has no built-in barcode reader (Safari/iOS).
- `fonts/` – Figtree by Erik Kennedy, SIL Open Font License 1.1 (via @fontsource/figtree).

To update: `npm install barcode-detector @fontsource/figtree` in a scratch folder and copy the same files.
