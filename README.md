# The World Today — Saturday 21 November 2026 in one image

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![Rank](https://make.fun/badge/news-image-20261121/Rizaltri13/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![Reward](https://make.fun/badge/news-image-20261121/Rizaltri13/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

A make.fun bounty entry for
[news-image-20261121](https://make.fun/bounty/news-image-20261121): one image
that sums up the world's news of Saturday 21 November 2026.

## The program

`main.py` (Python 3, standard library only, no network) draws a 1024×1024
newspaper front page — masthead "THE WORLD TODAY", a red date band, a large
hero panel for the lead story, six story tiles with small pictograms, and a
bottom ticker of shorter items — and encodes it as a PNG with a hand-rolled
encoder (`zlib` + `struct`). The hero panel is a generated illustration of
missiles over Poland at pre-dawn (`hero.png`, decoded here with a small PNG
reader); every letter on the page comes from a hand-typed 5×7 bitmap font,
so the text stays sharp and the output is fully deterministic: two runs
produce byte-identical files.

Run it with:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Verified 21 Nov 2026: two runs write byte-identical output
(sha256 `29743fa7a6cdfef1d97ddfc29e8c81d77900f5215474b1fa71102706de6674d0`,
487,593 bytes, 1024×1024 PNG, under the 1 MiB cap).

## The day's stories

- **Lead — Russian missiles hit Poland.** Two missiles and a suspected drone
  come down in south-east Poland during Moscow's biggest overnight attack on
  Ukraine; PM Tusk calls it a deliberate provocation and NATO calls it a
  grave violation of Polish airspace. (Sources: AP, The Times, CBS)
- **World court: Myanmar guilty of genocide.** The ICJ rules 9-6 that Myanmar
  committed genocide against the Rohingya in 2017 and orders reparations.
  (Sources: HRW, CNN, WSJ)
- **Wall St rout: S&P into correction.** The S&P falls 3.7% and the Nasdaq
  5.3% in its worst week since 2020 as the AI rally unwinds; Nvidia -14%.
  (Sources: Investopedia, WSJ, NPR)
- **Cyclone Akvan hits Odisha.** The storm crosses the coast near Gopalpur
  with 80 km/h winds after 300,000 people are evacuated. (Source: IMD)
- **UK and EU sign new deals.** PM Burnham signs pacts on food trade, carbon
  markets and youth mobility at a Brussels summit. (Source: wire reports)
- **Summit ends with little to show.** Trump, Xi and Putin leave their first
  trilateral meeting with few concrete results. (Source: wire reports)
- **Four nations demand Gaza aid access.** Australia, Canada, Italy and the
  UK call on Israel to let aid in as floods worsen the crisis.
  (Source: wire reports)
- **Ticker:** Bolsonaro taken to hospital · Palisades fire arsonist convicted
  · France protests enter a fourth weekend · COP31 enters its final stage ·
  Venezuela oil revenue report: $12bn · India fight back in Wellington.
  (Sources: wire reports)
