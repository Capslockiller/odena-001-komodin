---
yazan: codex
model: gpt-6.1-sol
---

# Molly's Nightstand

## Olgular — kaynak: tarif.md, kontrol.json ve kayıtlı dosya kontrolü

- Teslim: `sonuc.blend`; 12 geometrik parça, tamamı `Molly's Nightstand` koleksiyonunda. Birim metre. Kameralar ayrı `Preview cameras` koleksiyonunda.
- Tabla planı 0,40 × 0,40 m; toplam yükseklik 0,80 m. Kulplar dahil dış derinlik yaklaşık 0,417 m.
- Gövde: alt genişlik yaklaşık 0,292 m, ortada 0,368 m, üstte 0,340 m; dört köşe yuvarlatılmış.
- Tabla: 0,050 m kalınlık; üstte 0,016 m yuvarlak profil, altta 0,004 m yükseklikte hafif pah.
- Çekmece paneli 0,185 m; kapak paneli 0,370 m; oran 1:2. Aralık 0,007 m. Paneller gövde bombesini izler, yüzeyden en çok 0,009 m taşar.
- İki kulp: 0,036 m çapında, 0,020 m derinliğinde basık topuz ve kısa mil. Dört ayak: dışarıda 0,10 m yükseklik, üstte yaklaşık 0,060 m genişlik; aşağı doğru daralır.

| Parça | Adet | Modifier |
|---|---:|---|
| Bombeli gövde | 1 | Yok; profil ve köşe yuvarlaklığı doğrudan mesh |
| Kalın tabla | 1 | Yok; yuvarlak üst ve pahlı alt profil doğrudan mesh |
| Çekmece / kapak ön paneli | 2 | Yok; eğrilik ve yumuşak kenarlar doğrudan mesh |
| Basık topuz | 2 | Yok; ölçeği uygulanmış UV sphere |
| Kulp mili | 2 | Bevel: 0,0015 m, 3 segment; Weighted Normal |
| Daralan ayak | 4 | Bevel: 0,002 m, 3 segment; Weighted Normal |

## Yöntem

`model.py`, Blender 5.2.2 ile yalnızca headless çalıştırıldı. Gövde ve tabla yuvarlatılmış kare kesitleri birbirine bağlayarak oluşturuldu. Panel yüzeyleri, gövdenin aynı genişlik/derinlik fonksiyonuna yerleştirilen iç içe konturlardan üretildi; arkaları da kapalıdır. Gövde, tabla, paneller, kulplar ve ayaklar ayrı nesnelerdir. Renk, malzeme veya doku atanmadı; önizlemeler Workbench'in nötr stüdyo gösterimiyle üretildi.

## Tasarım yorumları / belirsizlikler

Çizim bulunmadığından bombenin miktarı, tabla kalınlığı, kenar yarıçapları, kulp boyutu ve ayak kesiti yorumlandı. En geniş kesit gövdenin ortasına yerleştirildi. Ayaklar yumuşak köşeli kare kesitli seçildi. Tarif yalnızca görünen biçimi tanımladığından dolap içi, çekmece kutusu, ray ve menteşe mekanizması modellenmedi. Filmdeki özgün parçaya birebir benzerlik doğrulanmadı; kaynak yalnızca sözlü tarifti.

## Kontrol

Ön, yan ve çapraz renderlar tarifle görsel olarak karşılaştırıldı. İlk sürümde ayakların üst köşelerindeki taşma giderildi ve bombe merkezi aşağı alındı; son sürüm yeniden renderlandı. Ölçüler, 1:2 panel oranı ve koleksiyon yerleşimi kayıtlı `sonuc.blend` yeniden açılarak doğrulandı (`verify.py`). Değerlendirilmiş 12 mesh üzerinde malzeme slotu 0, iki yüzle paylaşılmayan kenar 0 (`kontrol.json`). Ayrı parçaların montaj birleşimlerinde küçük örtüşmeler vardır.

Önizlemeler: `onizleme_on.png`, `onizleme_yan.png`, `onizleme_capraz.png`.
