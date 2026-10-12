# Molly's Nightstand (Molly'nin Komodini) - Modelleme Raporu

## 1. Parça Listesi ve Hiyerarşi
Tüm parçalar gerçek dünya ölçeğinde (metre cinsinden) modellenmiş olup doğrudan **`Molly's Nightstand`** koleksiyonu altına yerleştirilmiştir. Modelde hiçbir malzeme, doku veya renk tanımlanmamış, salt geometri teslim edilmiştir.

| Parça Adı | Açıklama | Boyutlar (X, Y, Z / m) |
|---|---|---|
| `Tabletop` | Üst tabla (dolgun yuvarlak üst kenar, pahlı alt kenar, yuvarlatılmış köşeler) | 0.410 × 0.410 × 0.038 |
| `Cabinet_Body` | Gövde dolap (kare plan, dikey köşeleri yuvarlak, ortada şişkin, aşağı daralan) | 0.387 × 0.387 × 0.672 |
| `Drawer_Front` | Üst basık çekmece paneli (bombeli yüzey, yumuşak kenar/köşeler, öne taşan) | 0.342 × 0.020 × 0.180 |
| `Door_Front` | Alt kapak paneli (çekmecenin 2 katı yükseklikte, gövde eğimini izleyen) | 0.343 × 0.033 × 0.360 |
| `Drawer_Knob` | Çekmece kulpu (kısa silindirik mil üzerinde basık yuvarlak topuz) | 0.033 × 0.026 × 0.033 |
| `Door_Knob` | Kapak kulpu (kısa silindirik mil üzerinde basık yuvarlak topuz) | 0.033 × 0.026 × 0.033 |
| `Leg_Front_Left` | Sol ön ayak (kısa, kalın, aşağıya doğru daralan, yuvarlatılmış tabanlı) | 0.056 × 0.056 × 0.090 |
| `Leg_Front_Right` | Sağ ön ayak (kısa, kalın, aşağıya doğru daralan, yuvarlatılmış tabanlı) | 0.056 × 0.056 × 0.090 |
| `Leg_Back_Left` | Sol arka ayak (kısa, kalın, aşağıya doğru daralan, yuvarlatılmış tabanlı) | 0.056 × 0.056 × 0.090 |
| `Leg_Back_Right` | Sağ arka ayak (kısa, kalın, aşağıya doğru daralan, yuvarlatılmış tabanlı) | 0.056 × 0.056 × 0.090 |

**Genel Bounding Box:**
- Genişlik (X): 0.410 m (41.0 cm)
- Derinlik (Y): 0.431 m (43.1 cm - kulplar ve paneller dahil; gövde tabanı ~0.32 m, tabla 0.41 m)
- Yükseklik (Z): 0.800 m (80.0 cm tabla üstü dahil)

---

## 2. Parça Başına Modifiers
Tüm parçalarda temiz quad (dörtgen) topoloji ve yumuşak çizgi film / Pixar estetiği için Subdivision Surface iş akışı uygulanmıştır:

- **`Tabletop`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Cabinet_Body`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Drawer_Front`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Door_Front`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Drawer_Knob`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Door_Knob`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Leg_Front_Left`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Leg_Front_Right`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Leg_Back_Left`**: `Subdivision Surface` (Viewport: 1, Render: 2)
- **`Leg_Back_Right`**: `Subdivision Surface` (Viewport: 1, Render: 2)

---

## 3. Seçilen Yöntem ve Modelleme Yaklaşımı
1. **Parametrik & BMesh Destekli Temiz Dörtgen (Quad) Modelleme:**
   - Modelin organik bombeleri, köşelerin yumuşak kavisleri ve keskin olmayan kenarları rastgele kutu modelleme yerine matematiksel eğriler (Bézier / kuadratik profil fonksiyonları ve ışın-kavis kesişimleri) ile oluşturuldu.
   - Bu sayede gövdenin yüksekliğe göre şişkinliği ($Z=0.46$ m civarında maksimum $38.6$ cm) ve aşağıya doğru konik daralması ($32$ cm taban) pürüzsüz yüzey sürekliliği kazandı.

2. **Tabla Profil Çözümü:**
   - Tabla kenarı için tek bir genel pah yerine brief'te talep edilen asimetrik profil doğrudan geometriye işlendi: Üst kenarda dolgun ve yuvarlak bir pah ($R = 13$ mm fillet), alt kenarda ise $45^\circ$ eğimli hafif bir pah ($4$ mm chamfer).
   - Üst ve alt kapaklar eşmerkezli halka insetting yöntemiyle quad olarak kapatılarak Subdivision Surface altında pinching/kırışıklık oluşması engellendi.

3. **Ön Panellerin Bombeyi Takip Etmesi:**
   - Çekmece ($H=18$ cm) ve kapak ($H=36$ cm, çekmecenin tam 2 katı) panelleri gövdenin ön yüzey eğrisini hem dikeyde ($Z$) hem de gövde daralmasına bağlı olarak yatayda ($X$) birebir takip edecek şekilde parametrik olarak büküldü.
   - Paneller gövde ön yüzeyinden ~8 mm öne taşırılarak ("çok az dışarı taşan") belirgin gölge derinliği sağlandı.
   - Panellerin kenarlarına $3.5$ mm yuvarlatma, köşelerine ise $12$ mm kavis verilerek dost canlısı çocuk odası mobilyası formu yakalandı. Aralarında $8$ mm temiz ve sabit bir derz aralığı bırakıldı.

4. **Kulplar ve Ayaklar:**
   - Kulplar, basık yuvarlak topuz ve kısa silindirik gövde birleşimi olarak torna/lathe yöntemiyle oluşturuldu ve her panelin merkezine yerleştirildi.
   - Ayaklar, alt uçta zemine yumuşak basan kavisli pah, yukarı doğru gövde tabanına sağlam oturan konik daralan formda tasarlandı ve köşe radiuslarına yakın konumlandırıldı.

---

## 4. Brief'in Yoruma Bıraktığı Noktalar ve Alınan Tasarım Kararları
1. **"Yaklaşık 40 × 40 cm taban" İfadesi:**
   - Brief'te "yaklaşık 40 × 40 cm taban" ile "tabla dahil boyu 80 cm civarı, kare plan" denmiştir. Mobilya tasarımında taban genellikle zemin izdüşümünü ifade eder. Tabla gövdeden her yönden biraz taştığı için, tabla ölçüsü $41 \times 41$ cm olarak seçilmiş; gövde en şişkin yerinde $38.7 \times 38.7$ cm, aşağı doğru daralarak alt tabanda $32 \times 32$ cm ve ayak merkezlerinde ~ $27-30$ cm olarak kurgulanmıştır. Böylece genel kapladığı alan tam olarak ~40 cm bandında tutulmuştur.
2. **Kapak Kulpunun Konumu:**
   - Standart gardırop/komodin kapaklarında kulp çoğunlukla açılma kenarına yakın (sağ veya sol) konur. Ancak brief özellikle: *"Her panelin ortasında küçük yuvarlak, basık topuz kulp"* ifadesini kullanmıştır. Bu nedenle çekmecede olduğu gibi alt kapakta da kulp tam geometri merkezine ($X=0$, panelin dikey orta noktası) yerleştirilmiştir; bu durum Toy Story stilindeki sevimli, simetrik ve stilize çizgi film havasını güçlendirmiştir.
3. **Ayak Formu (Yuvarlak vs. Köşeli):**
   - Brief'te *"Altta dört kısa, kalın, aşağı doğru hafif daralan ayak; köşelere yakın"* denmiş, kesit belirtilmemiştir. Molly'nin odasındaki ahşap torna mobilya estetiğine ve oyuncak bebek odası havasına en uygun olan, tornalanmış konik yuvarlak ayak formu tercih edilmiş; zeminle temas eden alt kenarına yumuşak kavis verilmiştir.
4. **Panellerin Gövdeye Montaj İlişkisi:**
   - Brief'te panellerin *"gövdenin ön yüzünden çok az dışarı taşan, gövdenin bombesini izleyen"* yapıda olduğu belirtilmiştir. Bu durum kısmi bindirme (overlay) veya öne taşan panel olarak yorumlanmış; paneller gövde yüzeyinden 8 mm önde, arkası gövdeye temiz oturan ve aralarında 8 mm gölge aralığı bırakan bağımsız parçalar olarak modellenmiştir.
