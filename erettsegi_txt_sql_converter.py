import time
from os import listdir, getcwd
cwd = getcwd()

""" Beállítások, ha más lenne a forrás """
txt_szeparator = "\t" # régebbieknél ;
encoding = "ANSI"   # régebbiknél ANSI, de ha utf-8-bom konvertáld át utf-8-ra
""" Vége """

start = False

def error(uzenet):
    print('\033[91m' + uzenet + '\033[0m')
    exit()
def txt_fileok_mappaban(path):
    try:
        txt_file_list = [x for x in listdir(path) if x.endswith(".txt")]
        return txt_file_list
    except:
        error("Hibás útvonal!")

def confirm(txt_file_list):
    print(f"{len(txt_file_list)}db .txt található:", " ".join(txt_file_list))
    return input("Átkonvertálja ezeket? (y/n) ").lower() == "y"


# jelenlegi mappa átnézése
txt_fileok = txt_fileok_mappaban(cwd)
if not len(txt_fileok) == 0:
    start = confirm(txt_fileok)
    mas_mappa = False
else: # másik mappa megnézése
    print("Nincs .txt fálj ebben a mappában")
    mas_mappa = (input("Szeretne másik mappában átalakítani? (y/n): ").lower() == "y")
if mas_mappa:
    cwd = input("Adjon meg egy "+'\033[1m'+"teljes " +'\033[0m'+"útvonalat, pl: C:\\Users\\felhasz\\mappa \n")
    txt_fileok = txt_fileok_mappaban(cwd)
    if len(txt_fileok) == 0:
        error("Nincs .txt fálj ebben a mappában")
    start = confirm(txt_fileok)

if not start:
    exit()

start_time = time.perf_counter()
def meno_vonal(szo):
    fel = round((50-len(szo))/2)
    print("-"*fel+szo+"-"*fel)

meno_vonal("Adatok betöltése")

db_name = cwd.split("\\")[-1].strip("123456789_")  # mappanev
output_file = f"{cwd}\\{db_name}.sql"  # teljes utvonal + file
output_file = open(output_file, "w", encoding=encoding)  # file nyitas

tablak = [x.replace(".txt", "") for x in txt_fileok]  # .txt levagasa

class tabla:
    def int_resolve(self, int, neg):
        int = abs(int)
        if neg:
            return "boolean"
        value = {1:"boolean", 127: "tinyint", 32767: "smallint", 8388607: "mediumint", 2147483647: "int"}
        for idx, i in enumerate(value):
            if int <= i:
                return list(value.values())[idx]

    def null_a_vegen(self, adat):
        n = len(self.fejlec)
        for idx, sor in enumerate(adat):
            if len(sor) < n:
                for _ in range(n-len(sor)):
                    adat[idx].append("NULL")
        return adat
    def datatype_tipp(self, adat):
        '''
        szoveg = [varchar, maxhossz]
        datum = [date, szeparátor]
        int = [int, intfajta ]
        '''
        typelist = []
        for oszlop in range(len(self.fejlec)):
            len_max = 0
            if not adat[0][oszlop].replace("-", "").replace(".", "").isnumeric():  # str eset
                for sor in adat:  # max hossz keresése
                    if oszlop<=len(sor) and not sor[oszlop] == "":
                        if len(sor[oszlop].encode(encoding)) > len_max:
                            len_max = len(sor[oszlop].encode(encoding))
                typelist.append(["varchar", str(len_max)])
            elif adat[0][oszlop].count(".") == 2 or adat[0][oszlop].count("-") == 2:  # date eset
                if adat[0][oszlop].count(".") == 2:  # szeparátor keresése
                    typelist.append(["date", "."])
                    self.datumpont = True
                else:
                    typelist.append(["date", "-"])
            elif adat[0][oszlop].lstrip("-").isnumeric(): # int eset
                negativ_egy = False
                for sor in adat:
                    if oszlop<=len(sor) and not sor[oszlop] == "" and not sor[oszlop] == "NULL":
                        if int(sor[oszlop]) > len_max:
                            if sor[oszlop] == "-1":
                                negativ_egy = True
                            len_max = int(sor[oszlop])
                typelist.append(["int", self.int_resolve(len_max*2, negativ_egy)])
            else:
                error("nincs ilyen tipus:( vagy üres az első sor valamelyik eleme")
        return typelist

    def __init__(self, telj_utvonal):
        self.utvonal = telj_utvonal
        self.nev = telj_utvonal.split("\\")[-1]
        self.file = open(self.utvonal, encoding=encoding)
        self.fejlec = self.file.readline().strip().split(txt_szeparator)
        self.datumpont = False
        self.adat = []
        for sor in self.file:
            self.adat.append(sor.strip().split(txt_szeparator))
        self.adat = self.null_a_vegen(self.adat)
        if len(self.fejlec) < 2:
            error(f"Kevesebb mint 2 oszlop! Hibás fálj: {self.utvonal}\nTalán rossz szeparátor vagy \"kódolás\" beállítva?")
        self.datatype = self.datatype_tipp(self.adat)
        self.file.close()
        if self.datumpont:
            self.dateidx = [idx for idx, x in enumerate(self.fejlec) if x[0]=="date"]
            for idx in self.dateidx:
                for idy in range(len(self.adat)):
                    self.adat[idy][idx] = self.adat[idy][idx].replace(".", "-")

tablak_class = []
for idx, t in enumerate(tablak):
    tablak_class.append(tabla(cwd + "\\" + txt_fileok[idx]))

print("Megvan!")  # vagyis reméljük
for tabla_class in tablak_class:
    meno_vonal(tabla_class.nev)
    for i in range(len(tabla_class.fejlec)):
        good = " ".join(tabla_class.datatype[i])
        print(f"{tabla_class.fejlec[i]}" + (50-len(tabla_class.fejlec[i]+good))*" " + good)
    print()

meno_vonal(db_name+".sql")
header = f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_hungarian_ci;\nUSE `{db_name}`;\n"
output_file.write(header)

def create_table(tabla_c, idx):
    fejlec = tabla_c.fejlec
    # create table
    out_str = f"CREATE TABLE `{tablak[idx]}` (\n"
    for oszlop in range(len(fejlec)):
        if tabla_c.datatype[oszlop][0] == "varchar":
            out_str += f"`{fejlec[oszlop]}` varchar({tabla_c.datatype[oszlop][1]}) COLLATE utf8mb4_hungarian_ci,\n"
        elif tabla_c.datatype[oszlop][0] == "int":
            out_str += f"`{fejlec[oszlop]}` {tabla_c.datatype[oszlop][1]},\n"
        elif tabla_c.datatype[oszlop][0] == "date":
            out_str += f"`{fejlec[oszlop]}` {tabla_c.datatype[oszlop][0]},\n"
    out_str = out_str[:-2] +"\n" # "," professzionális eltávolítása
    out_str += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_hungarian_ci;\n\n"
    #  INSERT INTO
    fej = ", ".join(["`" + x +"`" for x in fejlec])
    out_str += f"INSERT INTO `{tablak[idx]}` ({fej}) VALUES\n"
    non_int_idx = [idx for idx, x in enumerate(tabla_c.datatype) if x[0] == "varchar" or x[0] == "date"]
    for sor in tabla_c.adat:
        sor_lista = []
        out_str += "("
        for idy, oszlop in enumerate(sor):
            if not oszlop == "":
                if idy in non_int_idx:
                    sor_lista.append("'" + oszlop + "'")
                else:
                    sor_lista.append(oszlop)
            else:
                sor_lista.append("NULL")
        out_str += ", ".join(sor_lista) + "),\n"
    out_str = out_str.rstrip(",\n") + ";\n\n"
    return out_str

for idx, tabla_class in enumerate(tablak_class):
    output_file.write(create_table(tabla_class, idx))

end_time = time.perf_counter()
meno_vonal(str(round(end_time-start_time, 4))+" mp")
meno_vonal("Enter a kilépéshez")
a = input()