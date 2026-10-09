# Website assets

The pixel desktop illustration and icons are original inline SVGs in `index.html`
and `favicon.svg`, distributed under the project's Apache-2.0 license.

`pixel-font.css` embeds a 13,532-byte WOFF2 subset of Fusion Pixel Font,
12px proportional Simplified Chinese, release `2026.09.25`:

https://github.com/TakWolf/fusion-pixel-font/releases/tag/2026.09.25

The font and its upstream notices are covered by the SIL Open Font License 1.1.
Their complete license texts are included in `FONT-LICENSE.txt`.
The subset contains this page's Chinese characters and printable ASCII.
Other characters use the system fallback font. When adding Chinese copy,
regenerate the subset from the upstream release with FontTools and include the
updated HTML and JavaScript text. Keep the upstream license notices.
