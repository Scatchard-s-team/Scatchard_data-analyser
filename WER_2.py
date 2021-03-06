import numpy as np
from statistics import mean
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from pickle import load as read, dump as save
from os import listdir
from itertools import combinations
from copy import deepcopy as dc
from customowy_fit import get_r
comb_list = [[a/10000,b/100,c,d] for a in range(1,102,20)
                                for b in range(1,112,20)
                                for c in range(10,202,int(190/5))
                                for d in range(1,11,2)]
comb = [[0.1, 2.1 ,4.1, 6.1]] + list(combinations([i/10 for i in range(1,102,20)],4))
# comb = list(combinations([i/10 for i in range(1,502,100)],4))
# todo zakoentować nieużywane funckcje

class Dane:
    def __init__(self):
        # Lista zawierająca argumenty funkcji ( wartosci pionowe z tabeli danych z B)
        # dla szczura - jego wartosci    /   dla grupy - wartosci srednie
        self.Fy = []
        # Lista zawierająca wartosci funkcji  ( wartosci pionowe z tabeli danych z B/F)
        # dla szczura - jego wartosci    /   dla grupy - wartosci srednie
        self.semy_punktow = []
        # Lista zawierająca wartosci SEM dla kazdego punktu (only Fy) ( dlugosc pionu )
        # same 0.0001 dla szczorów
        self.semy_punktow_O = []
        # Lista zawierająca orginalne wartosci SEM dla kazdego punktu (only Fy)( dlugosc pionu )
        # same 0.0001 dla szczorów
        self.semy_punktow_V2 = []
        # Lista zawierająca wartosci SEM dla kazdego punktu (only Fy) ( dlugosc pionu )
        # same 0.0001 dla szczorów
        self.semy_outputow = {'k1': None, 'k2': None, 'r1': None, 'r2': None}
        # Słownik zawierający wartosci SEM : k1,r1,k2,r2
        # dla grupy - wartosci srednie
        self.nazwa = ''
        # string - nr szczura/nazwa grupy
        self.By = []
        self.semy_outputow_O = {'k1': None, 'k2': None, 'r1': None, 'r2': None}
        # Słownik zawierający orginalne wartosci SEM : k1,r1,k2,r2
        # dla grupy - wartosci srednie

        # Słownik zawierający wartosci: k1,r1,k2,r2
        # dla grupy - wartosci srednie
        self.outputy_O = {'k1': None, 'k2': None, 'r1': None, 'r2': None}
        # Słownik zawierający oryginalne wartosci: k1,r1,k2,r2
        # dla grupy - wartosci srednie
        self.parametry = []  # k1,k2,r1,r2
        # Lista zawierajaca parametry hiperboli: a, b, d, e
        self.parametry_O = []
        # Lista orginalnych parametrow
        self.ok = []
        # Lista zawierająca info o tym czy dany punkt (z By,Fy) jest uwzględniany przy liczeniu sem/ parametrow/outputow
        self.klasa = "Dane"
        self.true_Fy = []

    def obl_parametry(self, arg, wart):
        """
        dopasowuje parametry funkcji scatcharda do danych b i b/F -
        :return: zapisuje parametry jako self.parametry
        """
        #TODO NIE WYCH
        something_is = False
        nr_comb = 0
        max_r = 0
        while True:
            try:
                parametry_wejsciowe = np.array(comb[nr_comb])
            except:
                if something_is:
                    pass
                    # print("znaleziono nieoptymalne parametry")
                else:
                    print("NIE znaleziono optymalnych parametrów")
                break
            nr_comb += 1
            # print(comb[nr_comb])
            try:
                # if len(arg) <= 4 or len(wart) != len(arg):
                # print(len(arg),len(wart))
                # if len(arg) <= 2:
                #     print(self.nazwa, self.zwrot_ok(), len(self.szczury))
                parametry = curve_fit(scatchard_curv, arg, wart, p0=parametry_wejsciowe, bounds=[0, 300])[0]
                r = get_r(*self.zwrot_ok()[0:2],parametry)
                if r > max_r:
                    max_r = r
                    self.parametry = dc(parametry)
                if r >= 0.98:
                    with open("optimal_start_params.txt",'a') as plik:
                        plik.write(str(parametry_wejsciowe) + '\n')
                    print('znaleziono optymalne parametry')
                    break
                something_is = True
                with open("good_start_params.txt",'a') as plik:
                    plik.write(str(parametry_wejsciowe)+'\n')

            except:
                pass


    def dezaktywuj_pkt(self, nr):
        '''
        -w grupie dezaktywuje punkt na wykresie końcowym - już nie aktualne - zmiana koncepcji
        (wykres końcowy nie ma sensu)
        - w szczurze dezaktywuje jeden z jego punktów
        :param nr: numer punktu od 0 - to chyba od prawej strony w osi x
        :return:
        '''
        self.ok[nr] = False

    def aktywuj_pkt(self, nr):
        '''
        analogicznie do powyższej
        :param nr:
        :return:
        '''
        self.ok[nr] = True

    # jedynie deklaracje:

    def obl_semy_outputow(self):
        pass

    def obl_sr_sem_byify(self):
        pass

    def obl_sr_By_Fy_i_semy_pkt_grupy(self):
        pass

    def obl_outputy_sr(self):
        pass

    def zwrot_ok(self):
        pass


class Grupa(Dane):
    def __init__(self):
        super().__init__()
        self.szczury = []
        self.klasa = "Grupa"
        self.outputy_sr = {'k1': None, 'k2': None, 'r1': None, 'r2': None}
        self.true_outputs = {'k1': None, 'k2': None, 'r1': None, 'r2': None}
        self.true_F_sems = []
        # Lista zawierajaca obiekty szczorow danej grupy

    def zwrot_ok(self):
        """
        - funkcja zmieniona --- (nie dziala przez to generowanie wykresów) - stara funkcja taka jak w szczurze
        numery aktywnych szczurów
        :return: [[numery aktywnych punktów], x4]
        """
        ok_nrs = [i for i in range(len(self.szczury)) if self.szczury[i].aktywnosc is True]
        return [ok_nrs, ok_nrs, ok_nrs, ok_nrs]

    def obl_outputy_sr(self):
        '''
        oblicza średnie wartości wyników końcowych końcowych robiąc średnią ze szczurów
        - to jej wyniki wedłóg nowej koncepcji są prawidłowe
        :return: zapisuje w self.outputy_sr
        '''
        il_szczurow = len(self.szczury)
        for out in self.outputy_sr:
            lista = [self.szczury[i].outputy[out] for i in range(il_szczurow) if self.szczury[i].aktywnosc == 1]
            self.outputy_sr.update({out: mean(lista)})

    def obl_sr_sem_byify(self):
        """
        oblicza srednie wartosci SEM by i fy z aktywnych szczurow i je zapisuje
        todo zobaczyć czy jest potrzebna i czy aby nie psuje programu
        :return: None
        """
        by_punktow = list(zip(
            *[self.szczury[i].By for i in range(len(self.szczury)) if self.szczury[i].aktywnosc == 1]))
        fy_punktow = list(zip(
            *[self.szczury[i].Fy for i in range(len(self.szczury)) if self.szczury[i].aktywnosc == 1]))
        self.By = [sum(i) / len(i) for i in by_punktow]
        self.Fy = [sum(i) / len(i) for i in fy_punktow]
        self.semy_punktow = [sem(lista) for lista in fy_punktow]

    def obl_semy_outputow(self):
        """
        zapisuje semy outputow uwzgledniajac aktywne szczury
        :return:none
        """
        outputs_dict = {'k1': None, 'k2': None, 'r1': None, 'r2': None}
        il_szczurow = len(self.szczury)
        for out in outputs_dict:
            lista = [self.szczury[i].outputy[out] for i in range(il_szczurow) if self.szczury[i].aktywnosc == 1]
            self.semy_outputow.update({out: sem(lista)})

    def obl_sr_By_Fy_i_semy_pkt_grupy(self):
        '''
        oblicza i zaapisuje srednie wartosci by i fy dla danej grupy na podstawie danych w szczurach
        uwzglednia zmiany
        - funkcja nieaktualna - służyla do wykresu końcowego
        :return:
        '''
        sr_by = []
        sr_fy = []
        semy_fy = []
        for nr_pkt in range(len(self.szczury[0].By)):
            sumab = 0
            sumaf = 0
            listaf = []
            il_szczurow = len(self.szczury)
            for szczur in self.szczury:
                # if szczur.ok[nr_pkt] is False:
                #     print(szczur.nazwa, nr_pkt)
                if szczur.aktywnosc and szczur.ok[nr_pkt]:
                    sumab += szczur.By[nr_pkt]
                    sumaf += szczur.Fy[nr_pkt]
                    listaf.append(szczur.Fy[nr_pkt])
            sr_by.append(sumab / il_szczurow)
            sr_fy.append(sumaf / il_szczurow)
            semy_fy.append(sem(listaf))

        self.By = sr_by
        self.semy_punktow = semy_fy
        self.Fy = sr_fy

    def podsum_grupy(self):
        '''
        podsumowuje grupe printujac najwazniejsze dane czyli
        nazwa
        wartosci k i r wraz z semami
        pkazuje wyniki wszystkich szczurów .....
        :return: nic
        '''
        # grupa jako calosc
        print("GRUPA:", self.nazwa)
        # tworzenie stringa do sprintowania
        str2prt = ''
        szer_pola = 11
        po_przecinku: int = 6

        print(8 * ' ', "K1", "K2", "R1", "R2", sep=12 * ' ')
        for par in ('k1', 'k2', 'r1', 'r2'):
            str2prt += '{0[' + par + ']:' + str(szer_pola if par[1] == '2' else (szer_pola + 1)) \
                       + '.' + str(po_przecinku) + 'f}\t'
        print(4 * ' ' + "Wartości: ", end='')
        print(str2prt.format(self.outputy_sr))
        print(4 * ' ' + "   SEM-y: ", end='')
        print(str2prt.format(self.semy_outputow))

        # grupa jako kazdy osobno
        print(8 * ' ', "K1", "K2", "R1", "R2", sep=12 * ' ', end='')
        print(6 * ' ', "AKT")
        for nr, szczur in enumerate(self.szczury):
            str2prt = 'szcz_nr > ' + str(nr) + '<# '
            for par in ('k1', 'k2', 'r1', 'r2'):
                str2prt += '{0[' + par + ']:' + str(szer_pola) + '.' + str(po_przecinku) + 'f} | '
            print(str2prt.format(szczur.outputy), szczur.aktywnosc)

    def wykres_grupy(self):
        '''
        tworzy wykres grupy z errorbarami razem dla zmian(ziel) i bez nich(nieb)
        :param [zakres = False] format: [[xmin,xmax],[ymin,ymax]] gdy zamiast krotki flasz - automatyczne
         uwzglednia zakres lub nie
         - nieaktualna
        :return:
        '''
        # format errorbarow z daszkiem
        plt.rcParams.update({'errorbar.capsize': 3})
        plt.errorbar(self.By, self.Fy, self.semy_punktow_O, fmt='b*', ecolor='b')
        plt.errorbar(*self.zwrot_ok()[0:3], fmt='g*', ecolor='g')
        # rysowanie lini
        x = np.linspace(min(self.By), max(self.By), 500)
        y_zm = [scatchard_curv(i, *self.parametry) for i in x]
        y = [scatchard_curv(i, *self.parametry_O) for i in x]
        plt.plot(x, y, 'b')
        plt.plot(x, y_zm, 'g-')
        plt.legend(('bez zmian', 'ze zmianami'), loc='upper right')
        szer_pola = 9
        po_przecinku = 6

        print('pkt nr>' + 5 * ' ' + 'B/F' + 11 * ' ' + 'B' + 9 * ' ' + 'aktywność')
        for nr_pkt_w_szczurze, [b, f, ok] in enumerate(zip(self.By, self.Fy,
                                                           self.ok)):
            str2prt = ' {0:2}       '
            for os in ('1', '2'):
                str2prt += '{' + os + ':' + str(szer_pola) + '.' + str(po_przecinku) + 'f}|\t'
            str2prt += '{3}'
            print(str2prt.format(nr_pkt_w_szczurze, b, f, ok))

        numery = []
        for nr in range(len(self.By)):
            if self.ok[nr]:
                numery.append(nr)
        # bez tego sie robia brzydkie wykresy z naniesionymi cyframi - to zostawia tylko te w zakresie
        for nr, (x, y) in list(zip(numery, list(zip(*self.zwrot_ok()[:2])))):
            plt.text(x, y, str(nr))

        plt.title("grupa " + self.nazwa)
        plt.grid()
        plt.show()

    def wykr_porown_szczury(self, zmiany=True):

        '''
        funkcja pokazujaca wykresy wszystkich szczurow
        zmiany lub bez nich sa okreslane paremetrem
        :param nr: numer szczura do zestawienia z reszta
        :param zmiany: = True - pokazuje wykres ze zmianami, Flase - bez zmian
        :return: nic nie zwraca
        '''

        for ind, szczur in enumerate(self.szczury):
            if szczur.aktywnosc is True:
                kolor = 'g'

                x = np.linspace(min(szczur.By), max(szczur.By), 1000)
                parametry = szczur.parametry if zmiany else szczur.parametry_O
                y = [scatchard_curv(i, *parametry) for i in x]

                plt.plot(x, y, kolor + '-')
                # plt.plot(szczur.By, szczur.Fy, kolor + '*')
        if zmiany:
            plt.title('wykres aktywnych szczurów z grupy {}'.format(self.nazwa))
        else:
            plt.title('wykres wszystkich szczurów')
        plt.grid()
        plt.show()

    def obl_true_outputs(self):
        """
        funkcja służąca do obliczenia średnich wartości b i f dla grupy w celu lepszego rysowania wykresu
        - nieaktualna
        :return:
        """
        for szczur in self.szczury:
            szczur.true_Fy = [scatchard_curv(x, *szczur.parametry) for x in self.By]
        for nr in range(len(self.By)):
            Fy_od_danego_b = []
            for szczur in self.szczury:
                Fy_od_danego_b.append(szczur.true_Fy[nr])
            self.true_Fy.append(mean(Fy_od_danego_b))
            self.true_F_sems.append(sem(Fy_od_danego_b))
        self.obl_parametry(self.By, self.true_Fy)
        self.obl_output(self.parametry, self.true_outputs)  # todo gdzie to jest???
        self.obl_parametry(self.By, self.Fy)

    def aktualizacja_D(self):
        '''
        aktualizuje:
        - parametry
        - srednie outputy szczurów
        - semy wyników k i r
        :return:
        '''
        # self.obl_sr_By_Fy_i_semy_pkt_grupy()
        # self.obl_parametry(*self.zwrot_ok()[:2])
        self.obl_outputy_sr()
        self.obl_semy_outputow()


class Szczur(Dane):
    def __init__(self):
        super().__init__()
        self.outputy = {'k1': None, 'k2': None, 'r1': None, 'r2': None}
        self.aktywnosc = True
        self.klasa = "Szczur"
        # info czy dany szczur ma wplyw na wyniki grupy

    def dezaktywuj_szcz(self):
        """
        dezaktywuje szczura
        :return:
        """
        self.aktywnosc = False

    def zwrot_ok(self):
        """
        zwraca wartosci srednir by i fy punktow ktore sa aktywne
        :return: [aktywne_by, aktywne Fy, semy aktywnych Fy, numery aktywnych punktów]
        """
        by = [self.By[i] for i in range(len(self.By)) if self.ok[i]]
        fy = [self.Fy[i] for i in range(len(self.Fy)) if self.ok[i]]
        fy_s = [self.semy_punktow[i] for i in range(len(self.Fy)) if self.ok[i]]
        ok_nrs = [i for i in range(len(self.By)) if self.ok[i]]
        return [by, fy, fy_s, ok_nrs]

    def aktywuj_szcz(self):
        """
        aktywuje szczura
        :return:
        """
        self.aktywnosc = True

    def wykres_szczura(self, nazwa_grupy):
        '''
        rysuje wykres pojedynczego szczura ze zmianami (zielony) i bez nich (niebieski)
        :param nazwa_grupy: do napisania na wykresie
        :return: nic
        '''
        x = np.linspace(min(self.By) - 0.1, max(self.By), 1000)

        y = [scatchard_curv(i, *self.parametry) for i in x]
        y_O = [scatchard_curv(i, *self.parametry_O) for i in x]
        plt.plot(x, y_O, 'b-')
        plt.plot(x, y, 'g-')
        plt.legend(('bez zmian', "ze zmianami"), loc='upper right')

        numery = []
        for nr in range(len(self.By)):
            if self.ok[nr]:
                numery.append(nr)

        for nr, (x, y) in list(zip(numery, list(zip(*self.zwrot_ok()[:2])))):
            plt.text(x, y, str(nr))
        plt.plot(self.By, self.Fy, 'b*')
        plt.plot(*self.zwrot_ok()[:2], "g*")
        plt.title("szczur nr: " + str(self.nazwa) + " z grupy: " + nazwa_grupy)
        plt.grid()
        plt.show()

    def obl_output(self, parametry, flag=None):
        """
        oblicza k1,k2,r1,r2 i zapisuje w grupie
        :param parametry: a,b,d,e
        :return: None
        """
        # a, b, d, e = parametry
        # delta = abs(b ** 2 - 4 * a) ** (1 / 2)
        # k1 = (b - delta) / 2
        # k2 = b - k1
        # try:
        #     r1 = (d - e * k1) / (k1 ** 2 - k1 * k2)
        #     r2 = (e + k1 * r1) / (-k2)
        # except ZeroDivisionError:
        #     print("błąd k1 = k2 lub k2 = 0 - obl_output")
        #     r1 = (d - e * k1) / (k1 ** 2 - k1 * k2 + 0.001)
        #     r2 = (e + k1 * r1) / (-k2 + 0.001)
        nazwy_outputow = ['k1', 'k2', 'r1', 'r2']
        wart_outputow = [*parametry]
        for nr_out in range(len(nazwy_outputow)):
            if flag is None:
                # print(self.outputy,nazwy_outputow,wart_outputow)
                self.outputy[nazwy_outputow[nr_out]] = wart_outputow[nr_out]
            else:
                flag[nazwy_outputow[nr_out]] = wart_outputow[nr_out]


    def aktualizacja_S(self):
        """
        aktualizuje szczura:
        - parametry funkcji
        - wyniki końcowe
        :return:
        """
        self.obl_parametry(*self.zwrot_ok()[:2])
        self.obl_output(self.parametry)


class Punkt:
    """
    do ewentualnego zastosowania w przyszłości
    """

    def __init__(self):
        self.x: int = -1
        self.y: int = -1
        self.active: bool = True


def scatchard_curv(x, k1, k2, r1, r2):
    """
    warring for absolute delta
    oblicza wartość funkcji scatcharda w x
    :param x: argument
    :params a, b, c, d: function parameters
    :return: value of the scatchard function
    """
    a = k1 * k2
    b = k1 + k2
    d = -k1 * k2 * (r1 + r2)
    e = -k1 * r1 - k2 * r2
    A = 1
    B = e + b * x
    C = a * x * x + d * x
    delta = abs(B * B - 4 * A * C)
    return -B / (2 * A) + (delta ** (1 / 2)) / (2 * A)


def pdf_maker(grupy, zmiany=True):
    '''
    tworzy pdfy z danych w liscie grup
    - nieaktualna
    :param grupy: lista grup
    :param zmiany: wykesy bez/z zmianami
    :return: zapisuje pdfy
    '''
    plt.rcParams.update({'errorbar.capsize': 3})
    colors = ['r', 'b', 'g', 'm', 'y', 'k']
    colors_full_name = {'r': "czerwony", 'b': 'niebieski', 'g': 'zielony', 'm': 'fioletowy', 'y': 'zółty',
                        'k': 'czarny'}
    mx = max([max(grupa.zwrot_ok()[0]) for grupa in grupy])
    my = max([max(grupa.zwrot_ok()[1]) for grupa in grupy])
    x = np.linspace(0, mx, 500)
    print("grupa" + 9 * ' ' + "kolor")
    legenda = ''
    for c_nr, grupa in enumerate(grupy):
        color = colors[c_nr]
        param, By, Fy, semy = [grupa.parametry, grupa.zwrot_ok()[0], grupa.zwrot_ok()[1], grupa.zwrot_ok()[2]] if zmiany \
            else [grupa.parametry_O, grupa.By, grupa.Fy, grupa.semy_punktow]
        y = [scatchard_curv(i, *param) for i in x]
        plt.errorbar(By, Fy, semy, fmt=color + '*', ecolor=color)
        plt.plot(x, y, color + '-')
        legenda += str(grupa.nazwa) + " | " + str(colors_full_name[colors[c_nr]] + '\n')
    print(legenda + "\n legenda została zapisana w folderze wykresy pod nazwą wykresu z rozszezeniem '.txt'")
    nazwa = ''
    for grupa in grupy:
        nazwa += '+' + grupa.nazwa[3:]
    nazwa = nazwa[2:]

    plt.xlim(-1, mx + 1)
    plt.ylim(0, my * 10 / 9)
    # plt.legend("legenda", loc='upper right')
    plt.xlabel('Bound Insulin (nmol/l)')
    plt.ylabel("Bound/Free Insulin")
    plt.grid()
    # plt.title(nazwa)
    plt.savefig("./wykresy/" + nazwa + ".svg", quality=95, format='svg')
    with open("./wykresy/" + nazwa + ".txt", 'w') as plik_txt:
        plik_txt.write(legenda)
    plt.show()


def zapis_grup(grupy, par=None):
    """
    zapisuje binarny plik grupy pod nazwą i ścieżką par
    :param grupy: słownik z grupami
    :param par: ścieżka
    :return:
    """
    if par is None:
        par = ["grupy"]
    with open(par[0] + ".bin", 'wb') as plik:
        save(grupy, plik)


def odczyt_grup():
    '''
    odczytuje grupy z pliku grupy.bin
    :return: grupy jako slownik
    '''
    with open("grupy.bin", 'rb') as plik:
        grupy = read(plik)
    return grupy


def sem(lista):
    '''
    oblicza sem zadanej listy z brzydkiego wzorku
    :param lista: lista wartosci
    :return: sem listy
    '''
    if len(lista) in (0, 1):
        raise ArithmeticError
    return (sum([(x - sum(lista) / len(lista)) ** 2 for x in lista]) /
            (len(lista) - 1)) ** (1 / 2) / len(lista) ** (1 / 2)


def wejscie_ok(string, min, max):
    '''
    zwraca podana wartosc jako int jezeli
     da sie ja zkonwertowac i jest w przedziale zamnietym <min,max>
      jak sie nieda lub jest z poza przedzialu to 0
    :param string: input
    :param min: minimalna wartosc
    :param max: maxymalna wartosc
    :return: int
    '''
    try:
        string = int(input(string))
        string = string if min <= string <= max else -1
    except:
        string = -1
    return string


def group_name(nr):
    """
    zwraca nazwe grupy z danym numerem do użycia w słowniku
    :param nr:numer grupy <1,8>
    :return:
    """
    return ["1 - GKC_w", "2 - GKR_w", "3 - SDC_w", "4 - SDR_w", "5 - GKC_m", "6 - GKR_m", "7 - SDC_m", "8 - SDR_m"][
        nr - 1]


def is_number(string: str) -> float:
    """
    zwraca wpisany float jak sie da a jak nie to False
    :param string: string do input()
    :return:
    """
    try:
        return float(input(string))
    except:
        return False


def restore():
    """
    pozwala załadować zrobioną wcześniej migawkę
    - zobaczyć czy działa
    :return: słownik grupy albo False jak coś poszło nie tak
    """
    if "restore" in listdir("DATA"):
        snapshots = listdir("DATA/restore")
        for nr, snap_name in enumerate(snapshots):
            print(nr, '. ', snap_name)
        sel_snapshot_nr = wejscie_ok("wybierz plik do załadowania z listy podajac jego numer >>\n", 0,
                                     len(snapshots) - 1)
        if sel_snapshot_nr != -1:
            with open("DATA/restore/" + snapshots[sel_snapshot_nr], 'rb') as plik:
                print('poprawnie załadowano plik ', snapshots[sel_snapshot_nr])
                return read(plik)
        else:
            print("niepoprawny numer!")
    else:
        print("nie ma folderu restore")
    return -1  # if something went wrong


def masakrator(grupa):
    """
    funkcja rozwiązująca scatcharda automatycznie...
    :return:
    todo: optymalizacja szczurów tak żeby było najmnejsze sem
    todo: lepsze kryteria - szczególnie sem
    todo: rozbić na mniejsze funkcje i skomentować
    0. stworzyć osobny plik grup
    1. dla każdego szczura odjąć pierw 1 potem do 3 losowych punktów i sprawdzić odchylenia od punktów
    - jak będą ok to zostawić dla minimalnej liczby punktów
    - obliczyć dla danego szczura parametry wyjściowe
    2.  z każdej grupy odjąć od 1 do max 1/3 szczórów i sprawdzić kiedy sem będzie najmniejsze
    """
    # todo zrobić dla 0 pkt i 0 szczurów
    grupa = dc(grupa)
    for szczur in grupa.szczury:
        # optymalizacja szczura
        amount_points = len(szczur.zwrot_ok()[0])
        max_nr_dezaktiv = int(amount_points / 3)
        min_r = [0] * max_nr_dezaktiv
        good_points_nrs = []
        reachable_points_nrs = szczur.zwrot_ok()[3]
        max_nr_dezaktiv = int(amount_points / 3) + 1 - (amount_points - len(reachable_points_nrs))
        for il_inactiv_points in range(1, max_nr_dezaktiv):
            good_points_nrs.append([])
            all_comb = list(combinations(reachable_points_nrs, il_inactiv_points))
            for comb in all_comb:
                for nr_punktu in comb:
                    szczur.dezaktywuj_pkt(nr_punktu)
                szczur.aktualizacja_S()
                par = szczur.parametry
                r = get_r(*szczur.zwrot_ok()[0:2], par)
                if r > min_r[il_inactiv_points - 1] and szczur.outputy['r1'] > 0 and szczur.outputy['r2'] > 0:
                    min_r[il_inactiv_points - 1] = r
                    good_points_nrs[il_inactiv_points - 1] = [comb,r]
                for nr_punktu in comb:
                    szczur.aktywuj_pkt(nr_punktu)
                szczur.aktualizacja_S()
        # końcowy wybór punktów
        for nrsy_punktow, r in good_points_nrs:
            if r >= 0.99:
                for nr_punktu in nrsy_punktow:
                    szczur.dezaktywuj_pkt(nr_punktu)
                    minim_r = r
                break
        else:
            good_points_nrs_sorted = sorted(good_points_nrs, key=lambda x: x[1],reverse=True )
            for nr_punktu in good_points_nrs_sorted[0][0]:
                szczur.dezaktywuj_pkt(nr_punktu)
            minim_r = good_points_nrs_sorted[0][1]

        szczur.aktualizacja_S()
        print('szczur nr.',szczur.nazwa,'z grupy',grupa.nazwa,'zmasakrowany. R =',minim_r)
        print(szczur.outputy,szczur.parametry)
        szczur.wykres_szczura('gr1')


    reachable_szczurs_nrs = grupa.zwrot_ok()[3]
    amount_szczurs = len(grupa.szczury)
    max_nr_dezaktiv = int(amount_szczurs / 3)
    good_szczurs_nrs = []
    for il_inactiv_szczurs in range(1, max_nr_dezaktiv + 1):
        all_comb = list(combinations(reachable_szczurs_nrs, il_inactiv_szczurs))
        good_szczurs_nrs.append([])
        min_ratio = 9999
        for comb in all_comb:
            for nr_szczura in comb:
                try:
                    grupa.szczury[nr_szczura].dezaktywuj_szcz()
                except:
                    print(grupa.szczury, len(grupa.szczury), nr_szczura, comb)
            # try:
            grupa.aktualizacja_D()
            # except ArithmeticError:
            #     print(grupa.nazwa, grupa.zwrot_ok(), )
            sems = grupa.semy_outputow
            for sem_key in sems:
                ratio = sum([sems[sem_key]/grupa.outputy_sr[sem_key]])
                if ratio < min_ratio:
                # print("win", sems)
                    min_ratio = ratio
                    good_szczurs_nrs[il_inactiv_szczurs - 1] = [comb, ratio]
            for nr_szczura in comb:
                try:
                    grupa.szczury[nr_szczura].aktywuj_szcz()
                except:
                    print(grupa.szczury, len(grupa.szczury), nr_szczura, comb)
            grupa.aktualizacja_D()

    # końcowy wybór szczurów
    good_szczurs_nrs_sorted = sorted(good_szczurs_nrs,key=lambda x: x[1])
    print(good_szczurs_nrs_sorted)
    for szczur_nr in good_szczurs_nrs_sorted[0][0]: # regulacja
        # print(good_szczurs_nrs_sorted,szczur_nrs)
        # szczur_nrs = szczur_nrs if type(szczur_nrs) == list else [szczur_nrs]*2
        # for szczur_nr in szczur_nrs:
        #     print(szczur_nr)
        grupa.szczury[szczur_nr].dezaktywuj_szcz()
    try:
        grupa.aktualizacja_D()
    except:
        print('bład aktualizacji', grupa.zwrot_ok())
    # for szczur in grupa.szczury:
    # print(szczur.ok)
    print(grupa.nazwa, grupa.outputy_sr, grupa.semy_outputow, sep='\n', end='\n\n')
    # todo która ilosc punktow najlepsza dla danego szczura/grupy
    for nr, szczur in enumerate(grupa.szczury):
        tab = [True if i in szczur.zwrot_ok()[3] else False for i in range(len(szczur.By))]
        print('szczur nr: ', nr, ' : ', szczur.aktywnosc if szczur.aktywnosc is False else str(szczur.aktywnosc) + ' ',
              tab, szczur.outputy)
    return grupa


def mas_buff(grupa,mas_dict, now,ends,nr):
    mas_dict.update({grupa.nazwa: masakrator(grupa)})
    zapis_grup(mas_dict, par=['DATA/restore/grupy_masakrator' + '-'.join(
        list(map(str, [now.year, now.month, now.day, now.hour, now.minute, now.second])))])
    ends[nr] = 1