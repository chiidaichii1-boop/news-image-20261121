# The World, 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/chiidaichii1-boop/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/chiidaichii1-boop/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A newspaper front page for Saturday, 21 November 2026, drawn from scratch in
pure Python (standard library only). One lead story and seven more, spanning
regions and fields — every story verified against a named source and dated to
21 November 2026.

## The eight stories

1. **Lead — Ukraine:** Russia's "triple-tap" strike on Kryvyi Rih kills a
   seven-year-old boy and a 20-year-old paramedic; about 60 wounded. (CNN)
2. **Gulf:** Iran strikes a civilian industrial facility in Bahrain and two
   tankers are hit in the Strait of Hormuz. (AFP)
3. **Climate:** COP31 in Antalya runs into overtime as "fossil fuels" vanish
   from the draft deal. (AP)
4. **Mexico:** Military captures "El Chapo Isidro", an FBI top-ten most
   wanted fugitive, in Sinaloa; 11 killed in the raid. (Reuters)
5. **Peru:** A magnitude 6.9 earthquake shakes the Andes near Junin, felt in
   Lima; no casualties reported. (AP / USGS)
6. **Science:** The AI-assisted proof of the Riemann hypothesis passes its
   first independent checks; not yet confirmed. (Scientific American)
7. **Britain:** The UK-EU post-Brexit reset is sealed, then held up by a
   tuition-fees row. (The Times)
8. **Markets:** Wall Street falls into correction in an AI sell-off: S&P down
   3.7%, Dow down 950 points, Nvidia down 14%. (Reuters)

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` writes `out/entry.png` (1024x1024, under 1 MiB). It is
deterministic: two runs produce byte-identical PNGs.

---

<sub>Entered on [make.fun](https://make.fun/?ref=7g64vnx0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
