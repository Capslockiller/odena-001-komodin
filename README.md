# Odena 001: 8 yapay zekâ, aynı komodin (ham veri)

Videodaki testin bütün ham verisi: sözlü tarif, 24 deneme, bütün oylar ve hesap. Videodaki sayıların hepsi bu klasördeki verilerden yeniden üretilebilir.

## Test
- **Görev:** Toy Story eğitim serisindeki Molly'nin komodini (40 × 40 cm taban, 80 cm boy). Modeller referans modeli hiç görmedi, yalnız sözlü tarif aldı: [`gorev/tarif.md`](gorev/tarif.md), görev metni [`gorev/GOREV.md`](gorev/GOREV.md).
- **Kurulum:** Blender 5.2, arayüzsüz; deneme başına 45 dakika sınır; her model kendi önerilen ayarında, 3 deneme.
- **İnsan puanlaması:** 2 kişi, isimler gizli ikili karşılaştırma: "Bir 3D sanatçısı olarak hangisini teslim alırdın?" 56 çift × 2 = 112 oy → Bradley-Terry, Elo ölçeği, 1000 bootstrap; %95 güven aralıkları çakışanlar aynı kademe.
- **Yapay hakemler:** Gemini 3.8 Flash ve GPT 6.1 Sol aynı çiftlere baktı; her çift iki kez, sağ-sol değiştirilerek; iki cevap tutmazsa oy sayılmadı; kendi ailesine oy veremedi. Videodaki sıralama yalnız insan oylarından.
- **Benzerlik:** DINOv2 ile her deneme referansın dört açısına karşı (0–100, üç denemenin ortancası).

## Klasörler
| Klasör | İçerik |
|---|---|
| `gorev/` | Sözlü tarif ve görev metni (24 denemede bayt bayt aynı) |
| `kosular/<model>-yok-r<n>/` | 24 deneme: modelin yazdığı betikler, `sonuc.blend`, önizlemeler, `RAPOR.md`, model çıktısı (`cikti.json` / `cikti.jsonl`), `bitti.json` (süre) |
| `olcum/<deneme>/hucre.json` | Her denemenin ölçümü (geometri, token, maliyet, DINOv2/SigLIP2); `olcum/gorsel.json` toplu görsel benzerlik |
| `kor-paftalar/` | Oylayanların gördüğü isimsiz paftalar |
| `oylar/insan/` | İnsan oyları: `master.jsonl`, `dis-goz-1.jsonl` (lig girdisi: SOL/SAG/BERABERE) ve `cozulmus-*.jsonl` (her oyun hangi iki deneme olduğu açık) |
| `oylar/yapay/` | Yapay hakem oyları (`sol-med.jsonl`, `gemini.jsonl`), iki sunum sırasındaki ham cevaplarıyla |
| `oylar/` | `ciftler.json` (tam çift programı), `insan-ciftleri.json` (insanların oyladığı 56 çift), `gizli_harita.json` (kör kimlik → model/deneme) |
| `sonuc/` | Videodaki sonuç: `lig.json`, `LIG.md`; `kosu-ozeti.json` (süreler) |
| `kod/` | Hesap kodu: `arena/` (lig, Bradley-Terry, hakem), `oylama/coz.py`, `ozet.py`, `gorsel_benzerlik.py` |

Deneme klasörü adları: `opus-med` Opus 5.5 · `sonnet-med` Sonnet 5.5 · `haiku` Haiku 4.5 · `fable-med` Fable 5.1 · `astra-med` GPT 6 Astra · `sol-med` GPT 6.1 Sol · `gemini-high` Gemini 3.8 Flash · `gemini-pro` Gemini 3.1 Pro.

## Sonucu yeniden hesaplamak
Yalnız Python 3 standart kütüphanesi gerekir:

```
cd kod
python -m arena.lig --olcum ../olcum --harita ../oylar/gizli_harita.json --ciftler ../oylar/ciftler.json --insan-oy ../oylar/insan/master.jsonl --insan-oy ../oylar/insan/dis-goz-1.jsonl --yapay-oy ../oylar/yapay/gemini.jsonl --yapay-oy ../oylar/yapay/sol-med.jsonl --cikis ../yeniden
```

`yeniden/lig.json`, `sonuc/lig.json` ile birebir aynı çıkar (bootstrap tohumu 1). Yapay hakem dosyalarının sırası güven aralıklarını değiştirir; videodaki sıra yukarıdaki gibidir (önce Gemini). Puanlar ve kademeler sıradan etkilenmez.

`gorsel_benzerlik.py` (DINOv2/SigLIP2) ek paket ister (torch, transformers, Pillow) ve referans modelin render'larına ihtiyaç duyar; referans model bu klasörde yok. Ölçülen değerler `olcum/` içinde.

## Yayın için yapılan değişiklikler
- Oylayan adları rumuzla değiştirildi (`master`, `dis-goz-1`).
- Yerel disk yolları ve kullanıcı adı yer tutucuyla değiştirildi (`<tezgah>`, `<arena>`, `<calisma>`, `~`). `.blend` dosyalarında aynı uzunlukta değiştirildi.
- PNG'lerdeki Blender metaverisi (dosya yolu) silindi; pikseller aynı.
- Gemini gerekçe metinlerindeki bozuk Türkçe karakter kodlaması düzeltildi; kararlar değişmedi.
- Alınmayanlar: geçici dosyalar ve önbellekler, `.blend1` yedekleri, referans modelin kendisi ve render'ları, ara/parça hakem dosyaları.

## Bu test neyi ölçmez
Yalnız sözlü tariften modellemeyi ölçer; renk, malzeme, UV, sahne ve animasyonu ölçmez. Tek obje, tek tarif, iki oylayan: ortadaki modeller bu oy sayısıyla kesin ayrılamıyor.

Video: Odena (YouTube, @odenastudio)
