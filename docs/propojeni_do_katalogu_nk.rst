Propojeni do katalogu NK ČR
===========================
Kódy pro polí pro vyhledávání
*****************************

- **wrd** - slova ze všech popisných údaju (název, autoři, rok vyd., nakladatel, edice, klíčová slova atd.)
- **wtl** - slova z názvových údajů (název, název části, edice, originál atd.)
- **wau** - slova z údajů o autorech
- **wpb** - slova z údajů o nakladateli
- **wpp** - slova z údajů o místě vydání
- **wyr** - rok vydání
- **wkw** - předmět (klíčová slova)
- **sbn** - ISBN/ISMN
- **ssn** - ISSN
- **icz** - identifikační číslo záznamu
- **cnb** - číslo ČNB
- **sg** - signatura

Jedná se o kódy formulářů, tak jak by je bylo možné vybrat na webových stránkách.

Vyhledání záznamů – podle ISBN
------------------------------
    http://aleph.nkp.cz/X?op=find&request=sbn=978-80-7367-397-0&base=nkc

Vyhledání záznamů
-----------------

Podle autora a názvu
""""""""""""""""""""
 
    http://aleph.nkp.cz/X?op=find&request=wau=(Milan+Hejny)+and+wtl=(Dite+matematika)&base=nkc

(problémy s diakritikou, interpunkci, některými spojkami atd.)
    
    http://aleph.nkp.cz/X?op=find&request=wau=(Milan+Hejn%C3%BD)+and+wtl=(D%C3%ADt%C4%9B+a+matematika)&base=nkc

Podle nakladatele
"""""""""""""""""

    http://aleph.nkp.cz/X?op=find&request=wau=(Hejny)+and+wtl=(matematika)+and+wpb=Portal&base=nkc         

Nakladatel Grada
^^^^^^^^^^^^^^^^

    http://aleph.nkp.cz/X?op=find&request=wpb=Grada&base=nkc         

Případně pouze knihy
""""""""""""""""""""

    http://aleph.nkp.cz/X?op=find&request=wau=(Hejny)+and+wtl=(matematika)+and+wtp=bk&base=nkc

a další možné kombinace…

Odpověď
-------
Server vrátí odpověď, kde je uveden počet nalezených záznamů a kód množiny výsledků. Následně je možné stáhnout jeden nebo více vyhledaných záznamů v XML (formát `OAI-XML <http://www.openarchives.org/OAI/2.0/guidelines-oai_marc.htm>`_)
::

    http://aleph.nkp.cz/X?op=present&set_number=<kód množiny výsledků>&set_entry=1
    https://aleph.nkp.cz/X?op=present&set_number=39EUFDPANCBL5134N9UPNMPHFDEXPR2LR32GMP99R85TACTN5U

resp.::

    http://aleph.nkp.cz/X?op=present&set_number=<kód množiny výsledků>&set_entry=5,6,11
    
resp.::

    http://aleph.nkp.cz/X?op=present&set_number=<kód množiny výsledků>&set_entry=1-25
    http://aleph.nkp.cz/X?op=present&set_number=077285&set_entry=1-25

Průběh celé session
*******************
Dotaz na knihy vydavatele:

    http://aleph.nkp.cz/X?op=find&request=wpb=Grada&base=nkc

Což vrátí:
::   

    <find>
    <set_number>016513</set_number>
    <no_records>000004998</no_records>
    <no_entries>000002500</no_entries>
    <session-id>9A5HGMD6SMHBBX6NFDGTS6JD1GNK9JUFGQENM28Y6EDTL4RABD</session-id>
    </find>

Nyní získáme kódy dokumentů (přes url http://aleph.nkp.cz/X?op=present&set_number=016513&set_entry=1-100 anebo ve formatu marcxml http://aleph.nkp.cz/X?op=ill_get_set&set_number=016513&start_point=1&no_docs=500)

Použiji url http://aleph.nkp.cz/X?op=ill_get_set&set_number=016513&start_point=1&no_docs=2
::

  <ill-get-set>
  <doc-number>002475050</doc-number>
  <doc-number>002468257</doc-number>
  <no-docs>000000002</no-docs>
  <set-library>NKC01</set-library>
  <session-id>F3A9P757D16J84CULSGBTYSMDMYUXDDGDD8R6EEJIJIK9YDV4H</session-id>
  </ill-get-set>

Povšimněte si položek ``<doc-number>``. Čísla z nich je možné nyní využít pro stažení samotných záznamů.

Stažení záznamů (formát MARCXML)
--------------------------------

Funkce ``ill_get_set`` a ``ill_get_doc``. Stažení záznamů (po jednom) – např.:
  
* http://aleph.nkp.cz/X?op=ill_get_doc&doc_number=001810391&library=nkc01

Stažení záznamů (formát MAR OAI)
--------------------------------
Stažení záznamu podle systém. čísla (funkce ``find_doc``):

  http://aleph.nkp.cz/X?op=find_doc&doc_num=0018103916&base=nkc

nebo:

  http://aleph.nkp.cz/X?op=find_doc&doc_number=001810391&base=NAK

Funkce publish_avail
--------------------
Zjištění aktuální dostupnosti jednotek k danému záznamu (může být zadáno až 10 systém. čísel oddělených čárkami)

  http://aleph.nkp.cz/X?op=publish_avail&doc_num=002107662&library=nkc01
  
  resp.
  
  http://aleph.nkp.cz/X?op=publish_avail&doc_num=002107662,002124258,002105616&library=nkc01
  
  odpověď v češtině
  
  http://aleph.nkp.cz/X?op=publish_avail&doc_num=002107662,002124258,002105616&library=nkc01&con_lng=cze
  
  
Nastavení v tab_expand
----------------------
::

   X-AVAIL    expand_doc_bib_avail           AVA=DG,ZL,ND,RD
   X-AVAIL    expand_doc_del_fields          100##,245##,250##,260##,300##,AVA##
   
Standardně, je-li vyplněn status zprac. Jednotky, je jednotka nedostupná.  To je možné změnit přidáním parametru AVA=…, kde se uvedou všechny statusy, které dostupnost neblokují.