# Használat
1. A txt-ket tartalmazó mappa útvonalának megadása *vagy*
2. A szkriptet a mappába belehelyezve betölti a txt-ket
## Ha régebbi forrással dolgozunk a szkript felső sorában állítsuk át a szeparátort és az encodingot
*Bármely értelmes szövegszerkeztő kiírja az alsó sorban:*
![kép](https://github.com/CsomagoltWifi/emelt-info-txt-sql-konverter/assets/78613737/e56908ac-c3dc-4c12-a23f-4101903b6bea)
# A kód:
- felismeri az adattípusokat
- méretükhöz igazítja azokat
- a YYYY-MM-DD és YYYY.MM.DD dátumokat felismeri és a pontos verziót átalakítja

# TODO
- [ ] a forrás néha tartalmaz ' (vagy még nem ismert) karaktereket, amelyek tönkrevágják az sql szintaktikát (ritka)
- [ ] olvasható, átlátható legyen
- [x] működjön 
