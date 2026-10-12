# Molly's Nightstand - Tasarım Raporu

## Parçalar ve Uygulanan Modifier'lar
- **Body (Gövde):** Başlangıç olarak bir Cube oluşturulup `subdivide` edildi. Gövdenin bombesi, ortasının genişliği artırılıp alt kısmı daraltılarak Python'da yazılan bir deformasyon fonksiyonu ile sağlandı.
  - *Modifiers:* Bevel (dikey köşeleri yumuşatmak için), Subdivision Surface.
- **TopBoard (Üst Tabla):** Cube olarak başlatıldı. Köşe ve kenar detayları `bmesh` kullanılarak doğrudan verteks/kenar bazında yuvarlatıldı (üst kenara dolgun yuvarlak, alt kenara ince pah verildi).
- **Door ve Drawer (Kapak ve Çekmece):** Grid olarak oluşturulup, gövdedeki aynı bombe fonksiyonu kullanılarak kapak ve çekmecenin gövdeye paralel kavis alması sağlandı. 
  - *Modifiers:* Solidify (kalınlık vermek için), Bevel (yumuşak panel kenarları için), Subdivision Surface.
- **Knobs (Kulplar):** Çekmece ve kapağın üzerine, yüzey kavisini tam olarak karşılayacak uygun derinlikte yerleştirildi. Bir silindir mil ve Y ekseninde basıklaştırılmış bir küreden (basık topuz) oluşuyor.
- **Legs (Ayaklar):** Kalın birer silindir olarak köşelere yakın yerleştirildi ve Edit Mode düzeyinde alt verteksleri ölçeklendirilerek "aşağı doğru daralan" form elde edildi.

## Seçilen Yöntem
Arayüz kullanmadan (headless) çalıştığım için modellemeyi algoritmik olarak ele aldım. Geometriyi Boolean veya modifier stack üzerinden değil, direkt matematiksel fonksiyonlarla şekillendirmeyi tercih ettim (özellikle gövdenin bombesi ve panellerin bu bombeyi kusursuz takip etmesi için). Tüm parçalar `Molly's Nightstand` adlı koleksiyona eklendi. Geometrilerin kalitesini kontrol edebilmek için Cycles ile farklı açılardan render alıp orantıları ve kenar yumuşaklıklarını test ettim.

## Belirsizlikler / Tasarıma Bırakılan Detaylar
Brief (tarif) her ne kadar detaylı olsa da bazı milimetrik detayları kendi göz kararıma göre belirlemek durumunda kaldım:
- **Ayak ve Kulp Boyutları:** "Kısa kalın ayaklar" ve "küçük basık topuz kulplar" denildiği için oranları genel hacme yakışacak şekilde ölçeklendirdim. Ayaklara yaklaşık 10 cm, topuzlara ise yaklaşık 5 cm çap verdim.
- **Kapak/Çekmece Boşluğu:** İki bölüm arasındaki ince boşluk ölçüsü verilmediği için estetik duracak yaklaşık 2 cm'lik bir aralık (gap) tanımladım.
- **Malzeme:** Talimat gereği malzeme ve renk atanmamış olup, sadece formun ışıkla olan ilişkisini (pahları ve köşeleri) test edebilmek için temiz bir "Clay (kil)" malzemesi atanmıştır.
