Euler-Math package
====================

## Description

'Euler-Math.otf' (formerly named 'Neo-Euler.otf') is an OpenType version of
Hermann Zapf’s Euler maths font. It is the continuation of the Euler project
initiated by Khaled Hosny in 2009 and abandoned in 2016.
A style file 'euler-math.sty' is provided as a replacement of the
'eulervm.sty' package for LuaLaTeX and XeLaTeX users.

## Contents

* Euler-Math.otf     OpenType maths font
* euler-math.sty     LaTeX style file: replaces eulervm.sty for LuaTeX/XeTeX
* neo-euler.sty      For compatibility with the former name
* Euler-Math.pdf     Documentation in PDF format
* Euler-Math.ltx     LaTeX source of Euler-Math.pdf
* unimath-euler.pdf  Modified version of unimath-symbols.pdf
                     showing available Euler-Math symbols compared to
                     LatinModern, STIXTwo, Erewhon, TeXGyrePagella and Asana.
* unimath-euler.ltx LaTeX source of unimath-concrete.pdf
* README.md          (this file)

## Installation

This package is meant to be installed automatically by TeXLive, MikTeX, etc.
Otherwise, the package can be installed under TEXMFHOME or TEXMFLOCAL, f.i.
Euler-Math.otf in directory  texmf-local/fonts/opentype/public/euler-math/
and euler-math.sty in directory  texmf-local/tex/latex/euler-math/.
Documentation files and their sources can go to directory
texmf-local/doc/fonts/public/euler-math/

Don't forget to rebuild the file database (mktexlsr or so) if you install
under TEXMFLOCAL.

Finally, make the system font database aware of the Euler-Math font
(fontconfig under Linux).

## License

* The font 'Euler-Math.otf' is licensed under the SIL Open Font License,
Version 1.1. This license is available with a FAQ at:
http://scripts.sil.org/OFL
* The other files are distributed under the terms of the LaTeX Project
Public License from CTAN archives in directory macros/latex/base/lppl.txt.
Either version 1.3c or, at your option, any later version.

## Changes

* First public version: 0.20

* v0.21:
         - Delimiters, integrals, sum, prod etc. are now vertically
       centred by design on the maths axis (required by luametatex).
* v0.22:
     - Sizes of vertical variants of \lAngle, \rAngle, \langle and
       \rangle corrected.
     - Added stretchable integral for U+222B (usable with luametatex).
* v0.30:
     - *Name of the package changed from Neo-Euler to Euler-Math*;
         the former 'neo-euler.sty' style file has been kept for compatibility,
         it now loads 'euler-math.sty' and warns about the change.
     - Blackboard Bold glyphs added (derived from Michel Bovani's Fourier).
* v0.31:
     - Package now compatible with mathtools’ stretchable arrows.
     - \diagup and \diagdown moved from private area to U+27CB, U+27CD.
* v0.40:
    - Metrics of all "over" arrows and harpoons corrected.
    - Metrics of all "under" arrows and harpoons corrected.
    - Most horizontal arrows and harpoons are now stretchable.
* v0.41:
    - radicals corrected.
    - euler-math.sty: options handled by `l3keys` instead of `xkeyval`
    (requires a LaTeX kernel not older than 2022-06-01).
* v0.50:
    - Italic and BoldItalic alphabets filled with their upright
        counterparts as suggested by Ulrik Vieth.
    - Sans-serif alphabets (Latin and Greek) added, they are derived from
    IBMPlexSans text fonts.
    - Typewriter alphabet (Latin) added, derived from UMTypewriter-Regular.
* v0.51:
    - Fixed IsExtendedShape flags.
    - \mid (U+2223) and \parallel (U+2225) vertical variants changed.
    - OT features cvNN are now applied before ssty (applied last).
* v0.60:
    - Vertical variants of parentheses and braces redesigned to better
    match the shapes of the base glyphs.
    - Inconsistencies between vertical delimiter sizes fixed.
    - All sub/sup-scripts redesigned (they were far too wide).
* v0.61:
    - Fixed Game glyph (U+2141).
* v0.62:
    - Fixed superscripts for infty (U+221E).
    - Added glyph degree (U+00B0).
    - \hbar now differs from \hslash.
    - bar (U+0304), wideoverbar (U+0305), mathunderbar (U+0332) thicknesses'
    unified to default rule thickness.
    - Glyphs U+2032 to U+2037 and U+2057 (prime and co.) resized so that f.i.
    \(f'\), \(f\prime\) and \(f^{\prime}\) produce the same output.
* v0.63:
    - Math table fixes for horizontal composition of over/underbrace.
* v0.70:
  - Greek msans and mitsans glyphs added in Private Area.
  - Invisible Math operators (U-2061 to U+2064) added.
  - Compatibility with Typst v0.14: all glyphs used in vertical compositions
    now sit on the baseline.
  - Documentation fixes.
* v0.75:
  - Breaking change: two Greek glyphs (\Theta, \Phi) revised to match
    AMS Euler fonts v.3 (2008). Former shapes kept back through Character
    Variants 10 and 11.  Some others (\Gamma, \Sigma \kappa) softly tuned.
    Great thanks to Hans Hagen for providing the latest official glyphs.
  - Inconsistencies in over/under accents fixed, see
    https://tex.stackexchange.com/questions/759530/
  - over/underbrace: two size variants added for smoother width's variation.

---
Copyright 2009-2016  Khaled Hosny
Copyright 2022-2026  Daniel Flipo
E-mail: daniel (dot) flipo (at) free (dot) fr
