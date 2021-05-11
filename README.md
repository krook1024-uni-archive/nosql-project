# Business requirements

Keszitsuk el egy autoszerelo muhely nyilvantartasi rendszeret.

1. Legyen lehetoseg uj szerelot felvinni a rendszerbe. Taroljuk a kovetkezoket roluk:
  - Nev
  - Jelszo
2. Az egyes szerelok tudjanak bejelentkezni a rendszerbe.
3. Legyen lehetoseg uj jelszot kerni (az egyszeruseg kedveert beallitani) szerelokent.
4. Legyen lehetoseg tarolni a megrendeleseket:
  - Megrendeles sorszama
  - Auto rendszama (pl. ASD123)
  - Auto megnezese (pl. Opel Astra)
  - Auto gyartasi eve (pl. 2003)
  - Elkeszult-e?
5. Bejelentkezes utan legyen lehetoseg szerelesi cimletet felvinni, ami a kovetkezokbol all:
  - Cserelt alkatresz
  - Alkatresz es beszereles ara (HUF)
7. Bejelentkezes utan legyen lehetoseg az osszes megrendeles listazasara.
8. Bejelentkezes utan legyen lehetoseg a jelenlegi felhasznalonev lekerdezesere.
9. Bejelentkezes utan legyen lehetoseg lekerdezni a felvitt javitasokat es azok koltsegeit.   
10. A megrendeles statuszarol lehet erdeklodni, meg lehet tudni:
  - Az eddig cserelt alkatreszek
  - Varhato vegosszeg (HUF)
11. A megrendelest lehet osszesiteni, ahol:
  - kiszamoljuk a vegosszeget a cserelt alkatreszek aranak osszegekent
  - a megrendelest statuszat elkeszultre allitjuk
12. Az elkeszult megrendeleseket toroljuk 20 percenkent az adatbazisbol, amennyiben tobb, mint 200 ilyen van mar a memoriaban. A torolt rendeleseket mentsuk at egy relacios adatbazisba (ennek beszurasahoz szukseges SQL query-t irjuk le egy `queries_to_run` nevu fajlba, tetelezzuk fel, hogy egy masik, rajtunk kivul allo service elvegzi majd a beszurasokat).
13. Lehessen meghatarozni az 5 legjobb dolgozot, ugy, hogy ezt a cimet az kapja, aki a "legtobbet hozta a konyhara", azaz aki a legnagyobb ertekben cserelt alkatreszt osszesitve.
 
# Data structures

## `mechanic` (hash[])

- Username: str
- Password: str

## `mechanic:names` (set)

## `mechanic:tokens` (hash)

- *Key*: the token itself
- *Value*: the username of the mechanic

## `order` (hash[])

- Order_id: string (uuid4)
- Car_name: string
- Car_year_of_production: string
- Symptoms: string

## `order:ids` (set)

## `order:completed` (list)

List of completed `order_id`s.

## `order:notes` (zset)

- *Key*: Part_replaced
- *Value*: Cost

## `parts_replaced` (zset)

- *Key*: Mechanic_name
- *Value*: Total cost of parts replaced
