# coding: UTF-8

"""
This file is part of CFONB.

CFONB is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with CFONB.  If not, see <http://www.gnu.org/licenses/>.
"""
"""
 Coryright 2011, Stéphane Planquart <stephane@planquart.com>

 Créer un fichier de virement bancaire compatible avec "la structure des
 fichiers transmis par ETABAC 3 selon la norme CFONB"
 ce module prend en compte le format fourni par CFONB, il peut y avoir des
 différence en fonction de votre banque qui ne respecte pas totalement cette
 norme.
 "Seules les banques peuvent fournir le dessin exact des structures de
 fichier à jours"
"""


class Transfert:
    """
    Transfert example:

    >>> from datetime import date
    >>> d = date(2011,10,14)
    >>> a = Transfert()
    >>> a = a.setEmetteurInfos('2000121','affility','virement de test',503103,2313033,1212,d)
    >>> a.render()
    '0302        200012       14101affility                viremen                   E     503102313033                                                   1212       \\r\\n0802        200012                                                                                    0000000000000000                                          \\r\\n'

    """
    _emetteur = {}   # dict des infos sur l'emetteur du fichier de virement
    _total    = 0    # total des virements en centime d'euros
    _content  = ""   # contenu du fichier de virement sans le header et le footer
    _operation_type = "02"  # code opération par défaut pour un virement

    def setEmetteurInfos(self, num_emetteur, raisonsocial, reference,
                         guichet, num_compte, banque, datevir):
        self._emetteur['num_emetteur']   = str(num_emetteur)
        self._emetteur['raisonsocial']   = raisonsocial
        self._emetteur['reference']      = reference
        self._emetteur['guichet']        = guichet
        self._emetteur['num_compte']     = num_compte
        self._emetteur['banque']         = banque
        self._datevir                    = datevir.strftime('%d%m') + datevir.strftime('%y')[1:]

    def add(self, reference, raisonsocial, domiciliation,
            guichet, compte, montant, libelle,
            etablissement, balance=""):
        montant        *= 100       # passe le montant en centime d'euros
        self._total    += montant   # ajout le momtant au total des virements
        self._content  += self._add(reference, raisonsocial, domiciliation,
                                    guichet, compte, montant, libelle,
                                    etablissement, balance)

    def render(self, filename=None):
        content  = self._header()
        content += self._content
        content += self._footer()
        if filename is not None:
            f = open(filename, "wb")
            f.write(content)
            f.close()
        return content

    def _space(self, chaine, length, rpad=False, fill=""):
        return u"{0:{sign}{fill}{length}s}".format(str(chaine),
                                                   sign=">" if rpad else "<",
                                                   length=length,
                                                   fill=fill)[:length]

    def _header(self):
        # [zone A]
        content  = "03"
        # [zone B1]
        content += self._operation_type
        # [zone B2] Espace reserve 8 caracteres
        content += self._space('', 8)
        # [zone B3] numero emetteur (attribue par chaque etablisement 6 caracteres)
        content += self._space(self._emetteur['num_emetteur'], 6)
        # [zone C1-1] code CCD (virement à échéance "E-3")
        content += self._space('', 1)
        # [zone C1-2] Espace reserve 6 caracteres
        content += self._space('', 6)
        # [zone C1-3] date JJMMA
        content += self._datevir
        # [zone C2] Raison sociale du donneur d'ordre (24 caracteres max)
        content += self._space(self._emetteur['raisonsocial'], 24)
        # [zone D1-1] Reference virement sur 7 caracteres
        content += self._space(self._emetteur['reference'], 7)
        # [zone D1-2] Espace reserve 17 caracteres
        content += self._space('', 17)
        # [zone D2-1] Espace reserve 2 caracteres
        content += self._space('', 2)
        # [zone D2-2] Virement effectue en euro sur 1 caractere
        content += "E"
        # [zone D2-3] Espace reserve 5 caracteres
        content += self._space('', 5)
        # [zone D3] Code Guichet Emetteur 5 caracteres
        content += self._space(self._emetteur['guichet'], 5)
        # [zone D4] Numero de compte Emetteur 11 caracteres
        content += self._space(self._emetteur['num_compte'], 11)
        # [zone E] Espace reserve 16 caracteres
        content += self._space('', 16)
        # [zone F] Espace reserve 31 caracteres
        content += self._space('', 31)
        # [zone G1] code etablissement de la banque du donneur d'ordre
        #          5 caracteres
        content += self._space(self._emetteur['banque'], 5)
        # [zone G2] Espace reserve 6 caracteres
        content += self._space('', 6)
        content += "\r\n"
        return content

    def _footer(self):
        # [zone A]08 -> Code enregistrement (Entête Total)
        content  = "08"
        # [zone B1]02 -> Nature de l'enregistrement (virement à vue )
        content += self._operation_type
        # [zone B2]8 espaces
        content += self._space("", 8)
        # [zone B3] numéro émetteur (numéro attribué par chaque établissement à son client émetteur)
        content += self._space(self._emetteur['num_emetteur'], 6)
        # [zone C1]Réservée 12 caractères
        content += self._space("", 12)
        # [zone C2]Réservée 24 caractères
        content += self._space("", 24)
        # [zone D1]Réservée 24 caractères
        content += self._space("", 24)
        # [zone D2]Réservée 8 caractères
        content += self._space("", 8)
        # [zone D3]Réservée 5 caractères
        content += self._space("", 5)
        # [zone D4]Réservée 11 caractères
        content += self._space("", 11)
        # [zone E]Montant : les 16 positions contiennent le montant centimes
        #                  compris (00 s'il y a lieu) cadré à droite , non signé, complété à gauche par des zéros
        content += self._space(self._total, 16, rpad=True, fill="0")
        # [zone F]Réservée 31 caractères
        content += self._space("", 31)
        # [zone G1]Réservée 5 caractères
        content += self._space("", 5)
        # [zone G2]Réservée 6 caractères
        content += self._space("", 6)
        content += "\r\n"
        return content

    def _add(self, reference, raisonsocial, domiciliation,
             guichet, compte, montant, libelle,
             etablissement, balance=''):
        # [zone A]06 -> Code enregistrement (Entête destinataire)
        content  = "06"
        # [zone B1]02 -> Nature de l'enregistrement (virement à vue )
        content += self._operation_type
        # [zone B2]Espace réservé 8 caractères
        content += self._space("", 8)
        # [zone B3] numéro émetteur (numéro attribué par chaque établissement à
        #          son client émetteur)
        content += self._space(self._emetteur['num_emetteur'], 6)
        # [zone C1] référence (numéro facture par exemple) 12car
        content += self._space(reference, 12)
        # [zone C2] raison social du destinataure (24 caractères max)
        content += self._space(raisonsocial, 24)
        # [zone D1] domiciliation : désignation en clair du guichet et de la
        #         banque de domiciliataire (facultatif) sur 24  caractères maxi
        content += self._space(domiciliation, 24)
        # [zone D2] balance des paiements sur 8 caractères
        #         (réservé pour les salaires et pension)
        content += self._space("", 8)
        # [zone D3] Code Guichet 5 caractères
        content += self._space(guichet, 5)
        # [zone D4] Numéro de compte sur 11 caractères
        content += self._space(compte, 11)
        # [zone E]Montant : les 16 positions contiennent le montant centimes
        #        compris (00 s'il y a lieu) cadré à droite , non signé, complété à
        #        gauche par des zéros
        content += self._space(montant, 16, rpad=True, fill="0")
        # [zone F]Libellé : 31 caractères à la disposition du client émetteur
        #        pour indication du motif et des références de l'opération
        content += self._space("{}{}".format(" " if libelle else "", libelle), 31)
        # [zone G1]Code établissement destinataire 5 chiffres
        content += self._space(etablissement, 5)
        # [zone G2]Zone réservée de 6 caractères
        content += self._space("", 6)
        content += "\r\n"
        return content


class Debit(Transfert):
    """
    Debit implementation.
    Same as Transfert, but _operation_type is different.
    """

    _operation_type = "08"  # code opération par défaut pour un prélèvement
