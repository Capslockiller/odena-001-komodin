# Molly'nin Komodini Modelleme Raporu

## 1. Parçalar (Parts)

Model, gerçek dünya ölçeğinde (metre cinsinden) ve toplam 0.80 m (80 cm) yükseklik ile yaklaşık 40 × 40 cm taban/plan ölçülerinde modellenmiştir. Tüm parçalar `Molly's Nightstand` adlı koleksiyon içerisinde yer almaktadır.

1. **`Tabletop` (Tabla)**
   - **Ölçüler:** Genişlik 0.439 m, Derinlik 0.439 m, Kalınlık 0.042 m (Z: 0.758 m – 0.800 m).
   - **Form:** Gövdeden her yöne ~2.75 cm taşan kalın tabla. Dikey köşeleri yuvarlatılmış (R = 3.8 cm). Üst kenarı yuvarlak ve dolgun (R = 18 mm bullnose profil), alt kenarı ise 45° hafif pahlı (5 mm pah).
2. **`Body` (Gövde)**
   - **Ölçüler:** Genişlik 0.411 m (şişkin orta kesit), Derinlik 0.411 m, Yükseklik 0.678 m (Z: 0.080 m – 0.758 m).
   - **Form:** Kare planlı dolap gövdesi. Dikey köşeleri yumuşak yuvarlatılmış (keskin kenar yok). Yükseklik boyunca pürüzsüz kübik spline profil: tabanda 0.325 m'ye belirgin daralma, orta kesitte (~%49 yükseklikte) 0.405 m'ye şişkinleşme, üstte ise 0.380 m ile tablaya zarifçe bağlanma. Ön yüzde çekmece-kapak boşluğunun arkasında net gölge ayrımı sağlayan ince bir gölge kanalı.
3. **`Drawer_Front` (Çekmece Ön Paneli)**
   - **Ölçüler:** Genişlik 0.352 m, Kalınlık 0.015 m, Yükseklik 0.206 m (Z: 0.528 m – 0.734 m).
   - **Form:** Üstte basık çekmece paneli (en/boy oranı ~1.7:1). Gövdenin ön yüzünden ~1.1 cm dışarı taşar, gövdenin bombeli kavisini hem X hem Z ekseninde birebir izler. Kenarları yumuşak kavisli (pah/yuvarlatma).
4. **`Door_Front` (Kapak Ön Paneli)**
   - **Ölçüler:** Genişlik 0.357 m, Kalınlık 0.015 m, Yükseklik 0.414 m (Z: 0.106 m – 0.520 m).
   - **Form:** Çekmecenin yaklaşık 2 katı yüksekliğinde (0.414 / 0.206 ≈ 2.01) alt kapak paneli. Gövdenin aşağı doğru daralan bombeli formunu izler. Çekmece ile arasında 8 mm temiz boşluk bulunur.
5. **`Drawer_Knob` (Çekmece Kulpu)**
   - **Ölçüler:** Çap 0.040 m (40 mm), Derinlik 0.033 m, Z: 0.631 m (çekmece panelinin dikey ve yatay merkezinde).
   - **Form:** Kısa silindirik bir mil üzerinde basık, yuvarlak mantar/küre topuz kulp.
6. **`Door_Knob` (Kapak Kulpu)**
   - **Ölçüler:** Çap 0.040 m (40 mm), Derinlik 0.033 m, Z: 0.313 m (kapak panelinin dikey ve yatay merkezinde).
   - **Form:** Kısa silindirik bir mil üzerinde basık, yuvarlak mantar/küre topuz kulp.
7. **`Legs` (Ayaklar)**
   - **Ölçüler:** Yükseklik 0.080 m (8 cm, Z: 0.000 m – 0.080 m). Üst çap 6.6 cm, alt çap 4.8 cm. Dış yayılım 0.278 × 0.278 m.
   - **Form:** Dört adet kısa, kalın, aşağı doğru hafif daralan torna ayak. Gövdenin alt tabanının köşelerine yakın yerleştirilmiş; zeminle temas eden uçları yumuşak yuvarlatılmış kavisli pabuçludur.

---

## 2. Parça Başına Değiştiriciler (Modifiers per Part)

| Parça Adı | Değiştiriciler (Modifiers) | Parametreler & Amaç |
| :--- | :--- | :--- |
| **`Tabletop`** | `Subdivision Surface` | Level 1 (Render 2) — Üst dolgun yuvarlak kenarın ve alt pahın pürüzsüz geçişini sağlar. |
| **`Body`** | `Subdivision Surface` | Level 1 (Render 2) — Dikey köşelerin ve gövde bombeli yüzeylerinin organik, yumuşak eğrisini sağlar. |
| **`Drawer_Front`** | `Bevel` + `Subdivision Surface` | Bevel: Genişlik 7 mm, Segment 4, Limit Angle (40°), Miter Outer: Arc. Ardından Subsurf Level 1 (Render 2). Köşelerde büzüşme olmadan yumuşak yastık kenar formu üretir. |
| **`Door_Front`** | `Bevel` + `Subdivision Surface` | Bevel: Genişlik 7 mm, Segment 4, Limit Angle (40°), Miter Outer: Arc. Ardından Subsurf Level 1 (Render 2). |
| **`Drawer_Knob`** | `Subdivision Surface` | Level 1 (Render 2) — Torna topuz ve mil formunun ipeksi pürüzsüzlükte görünmesini sağlar. |
| **`Door_Knob`** | `Subdivision Surface` | Level 1 (Render 2) — Torna topuz ve mil formunun pürüzsüz görünmesini sağlar. |
| **`Legs`** | `Mirror` + `Subdivision Surface` | Mirror: X ve Y eksenlerinde simetri (4 ayak tek nesne). Ardından Subsurf Level 1 (Render 2). |

*Tüm nesnelerin transformasyon ölçekleri `(1.0, 1.0, 1.0)` olarak sıfırlanmıştır. Hiçbir nesneye malzeme (material) veya doku atanmamıştır (saf geometri).*

---

## 3. Seçilen Yöntem (Methodology)

- **Parametrik Headless Python Oluşturma:** Blender GUI açılmadan, saf `bmesh` ve `bpy` API'si üzerinden matematiksel eğrilerle parametrik üretim yapıldı.
- **Topoloji & Kenar Akışı (Edge Flow):**
  - Tüm modeller n-gon içermeyen (0 n-gon), manifold (0 manifold dışı kenar) ve gevşek tepe noktası bulunmayan (0 loose vertex) quad-dominant kafesler olarak inşa edildi.
  - Alt ve üst kapaklarda yüzey çökmesini önlemek için destek döngüleri (support loops) ve eşmerkezli quad halkaları kullanıldı.
  - Gövde kavisi, tabanda daralan (0.325 m), ortada şişen (0.405 m) ve tablaya dik bağlanan (0.380 m) C2 sürekliliğinde kübik polinom ile modellendi.
  - Paneller gövdenin çift eksenli kavisini birebir takip edecek şekilde üretildi ve açı-limitli `Bevel (Miter Arc)` + `Subsurf` ile yumuşatıldı.
  - Ayaklar için X/Y `Mirror` değiştiricisi kullanılarak parametrik simetri korundu.
- **Doğrulama ve İterasyon:** Headless Cycles motoruyla 4 farklı açıdan (3/4 perspektif, ön, yan ve detay yakın çekim) renderlar alındı, görsel hatalar (köşe büzüşmeleri, silüet geçişleri) iteratif olarak tespit edilip düzeltildi; ardından test tezgahının `istatistik.py` ve `tel.py` denetimleri çalıştırılarak doğrulandı.

---

## 4. Tarifin Belirsiz Bıraktığı Noktalar ve Yapılan Tercihler (Assumptions & Interpretations)

1. **Kapak Kulpunun Konumu:**
   - *Geleneksel mobilyalarda:* Dolap kapağı kulpları genelde kapağın açıldığı tarafa (sağ veya sol kenara yakın) konur.
   - *Briefteki ifade:* "Her panelin ortasında küçük yuvarlak, basık topuz kulp".
   - *Yapılan tercih:* Briefin "her panelin ortasında" ifadesine sadık kalınarak, kapak kulpu da çekmece gibi kapağın geometrik merkezine yerleştirildi. Bu simetrik yerleşim aynı zamanda Toy Story çocuk odası mobilyalarının hafif karikatürize/oyuncak havasını güçlendirdi.
2. **Ayak Kesiti (Yuvarlak vs. Kare):**
   - *Briefteki ifade:* "dört kısa, kalın, aşağı doğru hafif daralan ayak; köşelere yakın."
   - *Yapılan tercih:* Kesitin yuvarlak mı yoksa kare mi olduğu belirtilmemişti. Toy Story Molly odası ve Pixar çocuk mobilyası estetiğine en uygun olan torna yuvarlak konik ayaklar (tabanda yuvarlatılmış pabuçlu) tercih edildi.
3. **Gövde Ön Yüzü ve Panel Boşluğu Derinliği:**
   - *Briefteki ifade:* "İkisi de gövdenin ön yüzünden çok az dışarı taşan... aralarında ince bir boşluk."
   - *Yapılan tercih:* İki panel arasındaki boşluğun (8 mm) kil renderlarda ve gölgede net okunabilmesi için gövde karkasının ön yüzünde boşluğun arkasına denk gelen 8 mm'lik bir gölge kanalı eklendi. Böylece kapak ve çekmece ayrımı belirginleşti.
4. **Tabla Taşıntı Miktarı:**
   - *Briefteki ifade:* "gövdeden her yönden biraz taşan kalın bir tabla".
   - *Yapılan tercih:* Gövdenin en üst genişliği 38 cm iken, tabla 43.9 cm yapılarak her yönden ~2.75 cm dengeli bir saçak payı bırakıldı. Bu oran "sevimli ve dolgun" çizgi film orantısını sağladı.
