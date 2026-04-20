"""
Normteksten voor ISO 9001:2015 en ISO 27001:2022 (NEN-EN-ISO/IEC 27001:2023 nl).

Elke clausule bevat:
  normtekst     - letterlijke (verkorte) eis uit de norm, in het Nederlands
  interpretatie - praktische uitleg waarom de eis bestaat (voor een manager)
  bewijslast    - concrete documenten/artefacten die een externe auditor verwacht
"""

NORMTEKSTEN_9001 = {
    "4.1": {
        "normtekst": (
            "De organisatie moet de externe en interne aangelegenheden bepalen "
            "die relevant zijn voor haar doel en strategische richting en die "
            "van invloed zijn op haar vermogen om de beoogde resultaten van het "
            "kwaliteitsmanagementsysteem te behalen."
        ),
        "interpretatie": (
            "Je moet weten in welke omgeving je opereert voordat je processen "
            "kunt inrichten. Interne factoren zijn cultuur, capaciteit en "
            "systemen; externe factoren zijn markt, wet- en regelgeving en "
            "concurrentie. Zonder dit inzicht is elk kwaliteitsplan gebouwd op "
            "aannames."
        ),
        "bewijslast": [
            "Contextanalyse (SWOT, PESTEL of vergelijkbaar document)",
            "Notulen directiebeoordeling waarin context is besproken",
            "Strategisch plan of beleidsverklaring met verwijzing naar context",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Externe aangelegenheden bepaald (markt, wet/regelgeving, concurrentie, technologie)",
                "bewijslast": [
                    "PESTEL of marktanalyse met datum",
                    "Vermelding in directiebeoordeling of strategie-document",
                ],
            },
            {
                "id": "b",
                "eis": "Interne aangelegenheden bepaald (cultuur, capaciteit, kennis, systemen, waarden)",
                "bewijslast": [
                    "SWOT of interne analyse opgenomen in contextdocument",
                    "Bewijs dat interne factoren de KMS-scope beïnvloeden",
                ],
            },
        ],
    },
    "4.2": {
        "normtekst": (
            "De organisatie moet de relevante belanghebbenden bepalen en hun "
            "relevante eisen voor het kwaliteitsmanagementsysteem vaststellen. "
            "Deze informatie moet worden gemonitord en beoordeeld."
        ),
        "interpretatie": (
            "Klanten, medewerkers, leveranciers en toezichthouders hebben elk "
            "eigen verwachtingen. Door deze expliciet te maken voorkom je "
            "verrassingen en kun je gericht sturen. Een auditor wil zien dat "
            "je dit structureel bijhoudt, niet eenmalig."
        ),
        "bewijslast": [
            "Stakeholderregister met eisen per belanghebbende",
            "Bewijs van periodieke herziening (notulen, versiedatum)",
            "Koppeling tussen stakeholdereisen en KMS-scope of -doelstellingen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Relevante belanghebbenden geïdentificeerd (klanten, medewerkers, partners, toezichthouders, aandeelhouders)",
                "bewijslast": [
                    "Stakeholderregister met naam/groep en rol t.o.v. KMS",
                    "Voor Conduction: klanten, developers, partners (SIM/Procura), NEN/certificeringsinstantie",
                ],
            },
            {
                "id": "b",
                "eis": "Relevante eisen per belanghebbende vastgesteld (contractueel, wettelijk, impliciet)",
                "bewijslast": [
                    "Eisen per stakeholder gedocumenteerd (SLA, AVG, kwaliteitsverwachtingen)",
                    "Koppeling eisen aan KMS-scope of procesafspraken",
                ],
            },
            {
                "id": "c",
                "eis": "Informatie over belanghebbenden en hun eisen periodiek gemonitord en herzien",
                "bewijslast": [
                    "Versiedatum stakeholderregister of aantekening in directiebeoordeling",
                    "Bewijs van review bij contractwijziging of nieuwe klant",
                ],
            },
        ],
    },
    "4.3": {
        "normtekst": (
            "De organisatie moet de grenzen en toepasselijkheid van het "
            "kwaliteitsmanagementsysteem bepalen om de scope vast te stellen. "
            "De scope moet beschikbaar zijn als gedocumenteerde informatie."
        ),
        "interpretatie": (
            "De scope geeft aan welke onderdelen van de organisatie onder het "
            "certificaat vallen. Een te brede scope zonder dekking is net zo "
            "problematisch als een te enge scope die klanten misleidt. De "
            "redenering voor uitsluitingen moet aantoonbaar zijn."
        ),
        "bewijslast": [
            "Scopedocument (gedocumenteerde informatie)",
            "Motivatie voor eventuele uitsluitingen van clausules",
            "Certificaat of aanvraagdossier met scopeomschrijving",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Context (4.1) en stakeholdereisen (4.2) zijn meegenomen bij scopebepaling",
                "bewijslast": [
                    "Scopedocument verwijst naar contextanalyse en stakeholderregister",
                ],
            },
            {
                "id": "b",
                "eis": "Activiteiten, producten en diensten van de organisatie zijn beschreven",
                "bewijslast": [
                    "Scopeomschrijving in kwaliteitshandboek of certificaatdossier",
                ],
            },
            {
                "id": "c",
                "eis": "Eventuele uitsluitingen zijn gemotiveerd en beperkt tot clausules zonder invloed op conformiteit",
                "bewijslast": [
                    "Uitsluitingentabel met per clausule de motivatie (bijv. 8.3 indien geen O&O)",
                ],
            },
        ],
    },
    "4.4": {
        "normtekst": (
            "De organisatie moet de processen die nodig zijn voor het "
            "kwaliteitsmanagementsysteem en hun onderlinge samenhang bepalen, "
            "implementeren, onderhouden en continu verbeteren."
        ),
        "interpretatie": (
            "Het KMS is geen map met procedures; het is een samenhangend "
            "systeem van processen. Je moet weten welke inputs en outputs elk "
            "proces heeft, wie verantwoordelijk is en hoe processen op elkaar "
            "inwerken. Dit is de ruggengraat van de ISO 9001-aanpak."
        ),
        "bewijslast": [
            "Proceslandkaart of schildpad-diagram per kernproces",
            "Procesbeschrijvingen met inputs, outputs, eigenaar en KPI's",
            "Bewijs van procesmonitoring (metingen, dashboards)",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Processen bepaald: inputs, outputs, volgorde en wisselwerking",
                "bewijslast": [
                    "Proceslandkaart met alle KMS-processen en hun relaties",
                ],
            },
            {
                "id": "b",
                "eis": "Criteria, methoden en KPI's per proces vastgesteld",
                "bewijslast": [
                    "Procesbeschrijving of schildpad-diagram met meting en norm",
                ],
            },
            {
                "id": "c",
                "eis": "Verantwoordelijkheden en bevoegdheden per proces belegd",
                "bewijslast": [
                    "RACI of proceseigenaar per proces gedocumenteerd",
                ],
            },
            {
                "id": "d",
                "eis": "Risico's en kansen per proces geïdentificeerd (link naar 6.1)",
                "bewijslast": [
                    "Risicoregister of risicokolom in procesbeschrijving",
                ],
            },
            {
                "id": "e",
                "eis": "Processen continu verbeterd; gedocumenteerde informatie bewaard",
                "bewijslast": [
                    "Verbeterregister of versiehistorie van procesbeschrijvingen",
                ],
            },
        ],
    },
    "5.1": {
        "normtekst": (
            "Het topmanagement moet blijk geven van leiderschap en betrokkenheid "
            "bij het kwaliteitsmanagementsysteem door verantwoordelijkheid te "
            "nemen voor de effectiviteit ervan en kwaliteitsbeleid en "
            "-doelstellingen vast te stellen."
        ),
        "interpretatie": (
            "ISO 9001 verschoof verantwoordelijkheid bewust van de "
            "kwaliteitsmanager naar de directie. Als de directeur niet actief "
            "betrokken is, blijft kwaliteit een afdeling in plaats van een "
            "organisatiebrede cultuur. Een auditor toetst dit aan concrete "
            "acties, niet aan mooie woorden."
        ),
        "bewijslast": [
            "Notulen directiebeoordeling ondertekend door topmanagement",
            "Kwaliteitsbeleid ondertekend door directie",
            "Aantoonbare deelname van directie aan audits of verbeterprojecten",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Directie is eindverantwoordelijk voor KMS-effectiviteit (niet gedelegeerd aan kwaliteitsfunctionaris)",
                "bewijslast": [
                    "Notulen of actiepunten directie met expliciete KMS-betrokkenheid",
                ],
            },
            {
                "id": "b",
                "eis": "Kwaliteitsbeleid en doelstellingen afgestemd op strategische richting",
                "bewijslast": [
                    "Kwaliteitsbeleid ondertekend door directie, verwijzing naar strategie",
                ],
            },
            {
                "id": "c",
                "eis": "KMS geïntegreerd in bedrijfsprocessen (niet een los kwaliteitssysteem)",
                "bewijslast": [
                    "Bewijs dat KMS-eisen zijn opgenomen in werkprocessen (sprint, delivery)",
                ],
            },
            {
                "id": "d",
                "eis": "Klantgerichtheid geborgd: klanteisen en compliance worden bewaakt",
                "bewijslast": [
                    "Klanttevredenheidsmeting of klachtenregister met opvolging door directie",
                ],
            },
        ],
    },
    "5.2": {
        "normtekst": (
            "Het topmanagement moet een kwaliteitsbeleid vaststellen, "
            "implementeren en onderhouden dat passend is voor de context van "
            "de organisatie en een kader biedt voor kwaliteitsdoelstellingen."
        ),
        "interpretatie": (
            "Het kwaliteitsbeleid is de publieke belofte van de directie over "
            "wat kwaliteit voor de organisatie betekent. Het moet meer zijn dan "
            "een poster op de muur: medewerkers moeten het kennen en begrijpen, "
            "en het moet aantoonbaar doorwerken in doelstellingen."
        ),
        "bewijslast": [
            "Ondertekend kwaliteitsbeleid (gedocumenteerde informatie)",
            "Bewijs van communicatie aan medewerkers (intranet, toolbox, e-mail)",
            "Koppeling tussen beleid en meetbare kwaliteitsdoelstellingen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Kwaliteitsbeleid past bij de context en richting van de organisatie",
                "bewijslast": [
                    "Beleidstekst verwijst naar dienstverlening Conduction en klantfocus",
                ],
            },
            {
                "id": "b",
                "eis": "Beleid biedt kader voor meetbare kwaliteitsdoelstellingen",
                "bewijslast": [
                    "Aantoonbare link: beleidsstatement → concrete KPI of doelstelling",
                ],
            },
            {
                "id": "c",
                "eis": "Beleid bevat toezegging voor naleving van eisen én continue verbetering",
                "bewijslast": [
                    "Beleidstekst bevat expliciete verbeteringsclausule",
                ],
            },
            {
                "id": "d",
                "eis": "Beleid is gedocumenteerd, gecommuniceerd, begrepen en beschikbaar voor stakeholders",
                "bewijslast": [
                    "Versiedatum beleid, bewijs van communicatie (email/intranet), toegankelijk voor klanten op aanvraag",
                ],
            },
        ],
    },
    "5.3": {
        "normtekst": (
            "Het topmanagement moet de verantwoordelijkheden en bevoegdheden "
            "voor relevante rollen toewijzen, communiceren en begrijpelijk maken "
            "binnen de organisatie."
        ),
        "interpretatie": (
            "Onduidelijke verantwoordelijkheden zijn de meest voorkomende "
            "oorzaak van kwaliteitsproblemen. Iedereen moet weten wat zijn rol "
            "in het KMS is. Dit geldt speciaal voor de persoon die rapporteert "
            "aan topmanagement over KMS-prestaties."
        ),
        "bewijslast": [
            "Organogram met KMS-gerelateerde rollen",
            "Functiebeschrijvingen met expliciete KMS-verantwoordelijkheden",
            "Benoemingsbesluit of aanwijzingsbrief voor KMS-verantwoordelijke",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "KMS-rollen zijn toegewezen aan specifieke personen en gecommuniceerd",
                "bewijslast": [
                    "Organogram of RACI met KMS-verantwoordelijke, proceseigenaren",
                ],
            },
            {
                "id": "b",
                "eis": "KMS-verantwoordelijke rapporteert aan topmanagement over KMS-prestaties",
                "bewijslast": [
                    "Bewijs van rapportage: presentatie, memo of agenda directiebeoordeling",
                ],
            },
            {
                "id": "c",
                "eis": "Klantgerichtheid actief bevorderd door bevoegde personen",
                "bewijslast": [
                    "Functiebeschrijving met klantfocusverantwoordelijkheid (bijv. accountmanager, delivery lead)",
                ],
            },
        ],
    },
    "6.1": {
        "normtekst": (
            "De organisatie moet risico's en kansen bepalen die aangepakt moeten "
            "worden om te waarborgen dat het KMS de beoogde resultaten kan "
            "behalen, ongewenste effecten voorkomt en continue verbetering "
            "bewerkstelligt."
        ),
        "interpretatie": (
            "Risicomanagement in ISO 9001 is pragmatisch: je hoeft geen formeel "
            "risicoregister te hebben, maar je moet aantonen dat je nadenkt over "
            "wat mis kan gaan en wat je kansen zijn. Acties die je neemt moeten "
            "proportioneel zijn aan het risico."
        ),
        "bewijslast": [
            "Risicoregister of SWOT met risico's en kansen",
            "Actieplannen gekoppeld aan geïdentificeerde risico's",
            "Bewijs van evaluatie van de effectiviteit van maatregelen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Risico's en kansen bepaald vanuit context (4.1) en stakeholders (4.2)",
                "bewijslast": [
                    "Risicoregister of SWOT met verwijzing naar contextanalyse en stakeholderregister",
                ],
            },
            {
                "id": "b",
                "eis": "Acties gepland om risico's te beheersen en kansen te benutten",
                "bewijslast": [
                    "Actieplan per risico: maatregel, eigenaar, deadline",
                ],
            },
            {
                "id": "c",
                "eis": "Maatregelen geïntegreerd in KMS-processen en effectiviteit beoordeeld",
                "bewijslast": [
                    "Bewijs van periodieke risicoreview (directiebeoordeling of risicoaudit)",
                ],
            },
        ],
    },
    "6.2": {
        "normtekst": (
            "De organisatie moet kwaliteitsdoelstellingen vaststellen voor "
            "relevante functies, niveaus en processen. Doelstellingen moeten "
            "meetbaar zijn, worden gemonitord en worden gecommuniceerd."
        ),
        "interpretatie": (
            "Doelstellingen maken het kwaliteitsbeleid concreet en meetbaar. "
            "Zonder SMART-doelstellingen is er geen manier om te weten of het "
            "KMS werkt. Ze moeten ook echt worden bijgehouden, niet alleen "
            "jaarlijks worden opgeschreven."
        ),
        "bewijslast": [
            "Overzicht kwaliteitsdoelstellingen per afdeling of proces",
            "KPI-dashboard of rapportage met actuele meetwaarden",
            "Notulen directiebeoordeling met evaluatie doelstellingen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "SMART kwaliteitsdoelstellingen vastgesteld per relevante functie, niveau of proces",
                "bewijslast": [
                    "Doelstellingenoverzicht met meetcriterium, frequentie en eigenaar",
                ],
            },
            {
                "id": "b",
                "eis": "Per doelstelling: actieplan met wie, wat, wanneer, middelen en evaluatiemethode",
                "bewijslast": [
                    "Actieplan of projectplan per KPI, bijv. klanttevredenheid >8, doorlooptijd <X dagen",
                ],
            },
            {
                "id": "c",
                "eis": "Voortgang bewaakt, gecommuniceerd en bijgesteld waar nodig",
                "bewijslast": [
                    "KPI-rapportage of dashboard met historische trend, besproken in directiebeoordeling",
                ],
            },
        ],
    },
    "6.3": {
        "normtekst": (
            "Wanneer de organisatie bepaalt dat wijzigingen in het "
            "kwaliteitsmanagementsysteem nodig zijn, moeten deze wijzigingen "
            "op een geplande manier worden doorgevoerd."
        ),
        "interpretatie": (
            "Veranderingen in het KMS (nieuwe processen, herziene procedures) "
            "mogen niet ad hoc worden doorgevoerd. Je moet nadenken over doel, "
            "integriteit van het systeem, beschikbare middelen en "
            "verantwoordelijkheden voordat je wijzigt."
        ),
        "bewijslast": [
            "Wijzigingsbeheerproces of change management procedure",
            "Logboek van KMS-wijzigingen met datum, reden en goedkeuring",
            "Bewijs van communicatie van wijzigingen aan betrokkenen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Doel en potentiële gevolgen van KMS-wijzigingen zijn overwogen vóór implementatie",
                "bewijslast": [
                    "Wijzigingsverzoek of change request met impactanalyse",
                ],
            },
            {
                "id": "b",
                "eis": "Integriteit van KMS geborgd: samenhang tussen processen bewaard na wijziging",
                "bewijslast": [
                    "Bewijs dat afhankelijke processen zijn beoordeeld bij wijziging",
                ],
            },
            {
                "id": "c",
                "eis": "Middelen beschikbaar voor de wijziging; verantwoordelijkheden belegd",
                "bewijslast": [
                    "Goedkeuringsrecord wijziging met eigenaar en resourcetoewijzing",
                ],
            },
        ],
    },
    "7.1": {
        "normtekst": (
            "De organisatie moet de benodigde middelen bepalen en beschikbaar "
            "stellen voor het opzetten, implementeren, onderhouden en continu "
            "verbeteren van het kwaliteitsmanagementsysteem."
        ),
        "interpretatie": (
            "Middelen omvatten mensen, infrastructuur, meetapparatuur en kennis. "
            "De directie moet actief besluiten hoeveel middelen het KMS krijgt. "
            "Te weinig middelen is een directe bedreiging voor de effectiviteit "
            "van het systeem."
        ),
        "bewijslast": [
            "Budget of resourceplan voor KMS-activiteiten",
            "Overzicht infrastructuur en onderhoudsprogramma",
            "Bewijs van beschikbaarheid gekwalificeerd personeel",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Mensen: benodigde capaciteit bepaald en beschikbaar (intern + extern)",
                "bewijslast": [
                    "Personeelsplanning, inhuurbeleid of capaciteitsoverzicht",
                ],
            },
            {
                "id": "b",
                "eis": "Infrastructuur: hardware, software, tooling bepaald, onderhouden en beschikbaar",
                "bewijslast": [
                    "Infrastructuuroverzicht (cloud, laptops, tooling) met onderhoudsbeleid",
                ],
            },
            {
                "id": "c",
                "eis": "Werkomgeving: beheersmaatregelen voor menselijke en fysieke factoren bepaald",
                "bewijslast": [
                    "Werkplekbeleid, thuis/kantoorrichtlijn of ergonomiebeleid",
                ],
            },
            {
                "id": "d",
                "eis": "Meet- en monitoringsmiddelen: passend en aantoonbaar geschikt (gekalibreerd waar nodig)",
                "bewijslast": [
                    "Overzicht meetsystemen (tijdregistratie, kwaliteitstools) met validatie",
                ],
            },
            {
                "id": "e",
                "eis": "Organisatiekennis bepaald, onderhouden en beschikbaar gesteld",
                "bewijslast": [
                    "Kennisbeheersysteem (Confluence, wiki, kennisdeling-sessies) met actueel bewijs",
                ],
            },
        ],
    },
    "7.2": {
        "normtekst": (
            "De organisatie moet de benodigde competentie bepalen van personen "
            "die het kwaliteitsmanagementsysteem beïnvloeden, en waarborgen "
            "dat deze competentie aanwezig is."
        ),
        "interpretatie": (
            "Competentie gaat verder dan een diploma: het is de aantoonbare "
            "bekwaamheid om een taak goed uit te voeren. Je moet weten welke "
            "competenties nodig zijn, wie ze heeft en wat je doet als er een "
            "gat zit."
        ),
        "bewijslast": [
            "Competentiematrix per functie of rol",
            "Opleidingsplan en trainingsrecords",
            "Diploma's, certificaten of beoordelingsverslagen als bewijs",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Benodigde competenties bepaald per functie/rol die KMS beïnvloedt",
                "bewijslast": [
                    "Competentiematrix of functieprofiel met vereiste kennis/vaardigheden",
                ],
            },
            {
                "id": "b",
                "eis": "Medewerkers zijn aantoonbaar competent op basis van opleiding, training of ervaring",
                "bewijslast": [
                    "Opleidingsrecords, certificaten of beoordelingsverslagen per medewerker",
                ],
            },
            {
                "id": "c",
                "eis": "Acties genomen waar competentiekloof bestaat (training, coaching, herindeling)",
                "bewijslast": [
                    "Opleidingsplan met geplande trainingen en status, of POP per medewerker",
                ],
            },
            {
                "id": "d",
                "eis": "Gedocumenteerde informatie bewaard als bewijs van competentie",
                "bewijslast": [
                    "HR-dossiers of personeelsdatabase met opleidingen/certificeringen",
                ],
            },
        ],
    },
    "7.3": {
        "normtekst": (
            "Personen die werkzaamheden verrichten onder aansturing van de "
            "organisatie moeten zich bewust zijn van het kwaliteitsbeleid, de "
            "relevante doelstellingen en hun bijdrage aan de effectiviteit van "
            "het KMS."
        ),
        "interpretatie": (
            "Bewustzijn verschilt van training: medewerkers moeten begrijpen "
            "waarom kwaliteit belangrijk is en wat hun eigen rol daarin is. "
            "Een auditor kan medewerkers interviewen om dit te toetsen."
        ),
        "bewijslast": [
            "Communicatieplan of bewustwordingsprogramma",
            "Aanwezigheidsregistraties van toolboxen of briefings",
            "Bewijs van medewerkersbegrip (quiz, evaluatie of interview)",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Medewerkers zijn aantoonbaar op de hoogte van het kwaliteitsbeleid",
                "bewijslast": [
                    "Bewijs van communicatie beleid: onboarding-document, intranet, teamsessie",
                ],
            },
            {
                "id": "b",
                "eis": "Medewerkers kennen de relevante kwaliteitsdoelstellingen van hun rol",
                "bewijslast": [
                    "Doelstellingen opgenomen in functieprofiel of teamsprint-doelen",
                ],
            },
            {
                "id": "c",
                "eis": "Medewerkers begrijpen hun bijdrage aan KMS-effectiviteit",
                "bewijslast": [
                    "Bewijs van bewustwordingssessie, toolbox of teambespreking",
                ],
            },
            {
                "id": "d",
                "eis": "Medewerkers begrijpen de gevolgen van non-conformiteit met KMS-eisen",
                "bewijslast": [
                    "Gedragsregels, kwaliteitsbeleid of onboarding met gevolgen niet-naleving",
                ],
            },
        ],
    },
    "7.4": {
        "normtekst": (
            "De organisatie moet de interne en externe communicatie bepalen die "
            "relevant is voor het kwaliteitsmanagementsysteem, inclusief wat, "
            "wanneer, met wie en hoe wordt gecommuniceerd."
        ),
        "interpretatie": (
            "Slechte communicatie is een veelvoorkomende oorzaak van "
            "kwaliteitsproblemen. Door communicatie expliciet te plannen "
            "voorkom je dat cruciale informatie niet aankomt of verouderd is. "
            "Dit geldt zowel intern als naar klanten en leveranciers."
        ),
        "bewijslast": [
            "Communicatiematrix of communicatieplan",
            "Voorbeelden van uitgevoerde communicatie (nieuwsbrieven, notulen)",
            "Procedure voor externe communicatie over KMS-onderwerpen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Bepaald: wat over het KMS gecommuniceerd wordt (intern en extern)",
                "bewijslast": [
                    "Communicatiematrix met onderwerp, doelgroep en frequentie",
                ],
            },
            {
                "id": "b",
                "eis": "Bepaald: wanneer, met wie en hoe gecommuniceerd wordt en wie verantwoordelijk is",
                "bewijslast": [
                    "Communicatieplan of overlegstructuur (sprint reviews, retro's, klantoverleg)",
                ],
            },
        ],
    },
    "7.5": {
        "normtekst": (
            "Het kwaliteitsmanagementsysteem van de organisatie moet gedocumenteerde "
            "informatie bevatten die door de norm vereist wordt en die de "
            "organisatie zelf noodzakelijk acht voor de effectiviteit van het KMS. "
            "Gedocumenteerde informatie moet worden beheerd."
        ),
        "interpretatie": (
            "Documentbeheer gaat over het waarborgen dat de juiste versie op de "
            "juiste plek beschikbaar is en dat verouderde documenten worden "
            "ingetrokken. Het gaat niet om het maken van zoveel mogelijk "
            "procedures, maar om de documenten die er echt toe doen."
        ),
        "bewijslast": [
            "Documentbeheer procedure of DMS-instelling",
            "Lijst met gedocumenteerde informatie (documentregister)",
            "Bewijs van versiebeheer en goedkeuringsproces",
            "Bewijs van beheer van extern gedocumenteerde informatie",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Alle vereiste gedocumenteerde informatie aanwezig (norm-eis + eigen keuzes)",
                "bewijslast": [
                    "Documentregister met verwijzingen naar alle KMS-documenten",
                ],
            },
            {
                "id": "b",
                "eis": "Documenten geïdentificeerd, beschreven, opgemaakt en goedgekeurd",
                "bewijslast": [
                    "DMS-instelling (Drive, Confluence) met versiebeheer en eigenaar per document",
                ],
            },
            {
                "id": "c",
                "eis": "Toegang, bescherming, distributie, opslag en vernietiging geregeld",
                "bewijslast": [
                    "Toegangsrechtenbeheer Drive of DMS, bewaarbeleid (retentie), vernietigingsprotocol",
                ],
            },
        ],
    },
    "8.1": {
        "normtekst": (
            "De organisatie moet de processen die nodig zijn voor de realisatie "
            "van producten en diensten plannen, implementeren, beheersen en "
            "monitoren door criteria vast te stellen en gedocumenteerde informatie "
            "bij te houden."
        ),
        "interpretatie": (
            "Operationele planning zorgt ervoor dat de uitvoering van werk "
            "gecontroleerd verloopt en aan de eisen voldoet. Je moet criteria "
            "bepalen voor acceptatie en bewijs bewaren dat processen zijn "
            "uitgevoerd zoals gepland."
        ),
        "bewijslast": [
            "Operationele procedures of werkinstructies",
            "Productie- of dienstverleningsplannen",
            "Gedocumenteerde informatie als bewijs van procesuitvoering",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Criteria voor processen en acceptatie vastgesteld en gedocumenteerd",
                "bewijslast": [
                    "Definition of Done, acceptatiecriteria of kwaliteitsplan per project",
                ],
            },
            {
                "id": "b",
                "eis": "Processen worden beheerst uitgevoerd; bewijs bewaard",
                "bewijslast": [
                    "Sprint-records, delivery checklists of projectverslagen als procesuitvoerings-bewijs",
                ],
            },
            {
                "id": "c",
                "eis": "Uitbestede processen beheerst (zie ook 8.4)",
                "bewijslast": [
                    "Overzicht uitbestede processen + beheersmaatregelen (SLA, evaluatie)",
                ],
            },
            {
                "id": "d",
                "eis": "Geplande wijzigingen beheerst; onvoorziene wijzigingen beoordeeld op gevolgen",
                "bewijslast": [
                    "Change log of sprint-review records met geregistreerde scope-wijzigingen",
                ],
            },
        ],
    },
    "8.2": {
        "normtekst": (
            "De organisatie moet communiceren met klanten over informatie over "
            "producten en diensten, behandeling van vragen en orders, feedback "
            "inclusief klachten, en noodgevallen. Klanteisen en wettelijke eisen "
            "moeten worden bepaald en beoordeeld."
        ),
        "interpretatie": (
            "Je kunt geen kwaliteit leveren als je niet precies weet wat de "
            "klant verwacht. Eisen moeten worden bepaald vóór acceptatie van "
            "een order. Dit clausule-cluster dwingt je tot systematische "
            "klantcommunicatie en eisenbeheer."
        ),
        "bewijslast": [
            "Offerteproces of contractbeoordelingsprocedure",
            "Contracten of orderbevestigingen met vastgelegde eisen",
            "Klantcommunicatierecords (e-mails, verslagen klantgesprekken)",
            "Klachtenregister en afhandelingsrecords",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Productinformatie beschikbaar en klantcommunicatie georganiseerd",
                "bewijslast": [
                    "Diensten/productoverzicht beschikbaar voor klanten (website, offertedoc)",
                ],
            },
            {
                "id": "b",
                "eis": "Klanteisen bepaald vóór acceptatie van opdracht (inclusief wettelijke eisen)",
                "bewijslast": [
                    "Contractbeoordelingsprocedure of offerte-checklijst met eisenvalidatie",
                ],
            },
            {
                "id": "c",
                "eis": "Klanteisen beoordeeld; afwijkingen opgelost vóór contractaccept",
                "bewijslast": [
                    "Getekend contract of opdrachtbevestiging als bewijs van eisafstemming",
                ],
            },
            {
                "id": "d",
                "eis": "Klachten en feedback ontvangen, vastgelegd en afgehandeld",
                "bewijslast": [
                    "Klachtenregister of klanttevredenheidssysteem met afhandelingsrecords",
                ],
            },
        ],
    },
    "8.3": {
        "normtekst": (
            "De organisatie moet een proces opzetten, implementeren en onderhouden "
            "voor het ontwerpen en ontwikkelen van producten en diensten, inclusief "
            "planning, inputs, beheersmaatregelen, outputs en wijzigingsbeheer."
        ),
        "interpretatie": (
            "Ontwerpbeheersing voorkomt dat producten of diensten de markt "
            "bereiken zonder validatie. Het gaat erom dat ontwerpeisen helder "
            "zijn, dat verificatie plaatsvindt en dat wijzigingen worden "
            "beoordeeld op impact. Mag worden uitgesloten als er geen O&O is."
        ),
        "bewijslast": [
            "Ontwerp- en ontwikkelingsprocedure",
            "Ontwerp inputs en outputs per project (specificaties, tekeningen)",
            "Verificatie- en validatierapporten",
            "Overzicht ontwerpwijzigingen met goedkeuringsrecords",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Ontwerp- en ontwikkelingsproces bepaald en gedocumenteerd (planning, reviews, verificatie, validatie)",
                "bewijslast": [
                    "SDLC-beschrijving, sprint-cadans of productdevelopment-procedure",
                ],
            },
            {
                "id": "b",
                "eis": "Ontwerp-inputs bepaald: functionele eisen, wet/regelgeving, eerdere ervaringen",
                "bewijslast": [
                    "User stories, backlog of functionele specificaties per project als inputs",
                ],
            },
            {
                "id": "c",
                "eis": "Beheersmaatregelen: design reviews, verificatie en validatie uitgevoerd",
                "bewijslast": [
                    "Code review records, test-rapporten, acceptatietest met klant",
                ],
            },
            {
                "id": "d",
                "eis": "Ontwerp-outputs voldoen aan inputs; gedocumenteerd",
                "bewijslast": [
                    "Release notes of Definition of Done-check als bewijs outputs vs inputs",
                ],
            },
            {
                "id": "e",
                "eis": "Ontwerp-wijzigingen geïdentificeerd, beoordeeld, goedgekeurd en gedocumenteerd",
                "bewijslast": [
                    "Change log of bijgehouden sprint-backlog-wijzigingen met goedkeuring",
                ],
            },
        ],
    },
    "8.4": {
        "normtekst": (
            "De organisatie moet waarborgen dat extern geleverde processen, "
            "producten en diensten voldoen aan de gestelde eisen. Zij moet "
            "criteria bepalen voor beoordeling, selectie en monitoring van "
            "externe leveranciers."
        ),
        "interpretatie": (
            "Uitbesteding verschuift uitvoering maar niet verantwoordelijkheid. "
            "Je blijft verantwoordelijk voor wat een leverancier levert. "
            "Leveranciersbeheer moet risicogebaseerd zijn: kritieke leveranciers "
            "verdienen meer aandacht dan eenmalige toeleveranciers."
        ),
        "bewijslast": [
            "Leverancierslijst met kwalificatiestatus",
            "Leveranciersbeoordeling procedure en evaluatierecords",
            "Inkooporders of contracten met kwaliteitseisen",
            "Inspectierapportages of acceptatierecords van inkomende goederen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Selectie- en evaluatiecriteria voor externe leveranciers bepaald (risicogebaseerd)",
                "bewijslast": [
                    "Leverancierslijst met kwalificatiestatus en risicoklasse (bijv. SIM/Procura als kritiek)",
                ],
            },
            {
                "id": "b",
                "eis": "Beheersmaatregel proportioneel aan impact extern geleverde output op eindproduct",
                "bewijslast": [
                    "Bewijs van monitoring kritieke leveranciers (SLA-review, audit, beoordeling)",
                ],
            },
            {
                "id": "c",
                "eis": "Inkoopvereisten gecommuniceerd naar leveranciers (kwaliteitseisen, specificaties)",
                "bewijslast": [
                    "Contracten of inkooporders met expliciete kwaliteits- of service-eisen",
                ],
            },
        ],
    },
    "8.5": {
        "normtekst": (
            "De organisatie moet de productie en dienstverlening uitvoeren onder "
            "beheerste omstandigheden, inclusief beschikbaarheid van informatie, "
            "geschikte infrastructuur, monitoring, en maatregelen voor "
            "identificatie en traceerbaarheid."
        ),
        "interpretatie": (
            "Beheerste omstandigheden betekenen dat je weet wat je maakt, "
            "hoe je het maakt en dat je het kunt terugvinden als er iets "
            "misgaat. Traceerbaarheid is essentieel voor effectief "
            "probleemoplossen en terugroepacties."
        ),
        "bewijslast": [
            "Werkinstructies voor kernprocessen",
            "Productie- of servicerecords met identificatiegegevens",
            "Traceerbaarheidssysteem (batch, serienummer of equivalent)",
            "Registraties van vrijgave en afleveringsactiviteiten",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Beheerste omstandigheden: werkinstructies, goedgekeurde middelen, monitoring tijdens uitvoering",
                "bewijslast": [
                    "Werkinstructies of runbooks voor kernprocessen (deployments, klantdelivery)",
                ],
            },
            {
                "id": "b",
                "eis": "Identificatie en traceerbaarheid van outputs gedurende de uitvoering",
                "bewijslast": [
                    "Versienummering, sprint-labels of projectidentificatie in leverables",
                ],
            },
            {
                "id": "c",
                "eis": "Eigendom van klanten en externe partijen geïdentificeerd, beschermd en gerapporteerd",
                "bewijslast": [
                    "Data-verwerkersovereenkomst of klantdatabeheerbeleid (AVG)",
                ],
            },
            {
                "id": "d",
                "eis": "Bewaring en preservering van producten/diensten geregeld",
                "bewijslast": [
                    "Back-upbeleid, archivering of bewaarprotocol voor klantdata en leverables",
                ],
            },
            {
                "id": "e",
                "eis": "Activiteiten na levering bepaald (garantie, service, support, onderhoud)",
                "bewijslast": [
                    "Serviceovereenkomst, garantiebepaling of supportprocedure na oplevering",
                ],
            },
        ],
    },
    "8.6": {
        "normtekst": (
            "De organisatie moet op geplande momenten verificaties uitvoeren om "
            "te waarborgen dat aan de eisen voor producten en diensten is voldaan. "
            "Producten en diensten mogen pas worden vrijgegeven als aan alle "
            "gestelde eisen is voldaan."
        ),
        "interpretatie": (
            "Vrijgavebeheersing zorgt ervoor dat niets de klant bereikt zonder "
            "formele goedkeuring. De vrijgave moet worden gedocumenteerd inclusief "
            "wie heeft vrijgegeven. Dit is een direct controlemoment voor de "
            "auditor."
        ),
        "bewijslast": [
            "Inspectie- of testprocedure voor producten/diensten",
            "Keurings- of testrecords met handtekening vrijgavebevoegde",
            "Vrijgaveformulieren of digitale goedkeuringsrecords",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Verificaties op geplande momenten uitgevoerd om conformiteit te borgen",
                "bewijslast": [
                    "Test- of reviewrecords per sprint of oplevering (automated tests, peer review)",
                ],
            },
            {
                "id": "b",
                "eis": "Producten/diensten pas vrijgegeven als aan alle eisen is voldaan; wie/wanneer gedocumenteerd",
                "bewijslast": [
                    "Acceptatieformulier of digitale goedkeuring klant of productowner met datum en naam",
                ],
            },
        ],
    },
    "8.7": {
        "normtekst": (
            "De organisatie moet producten en diensten die niet voldoen aan de "
            "eisen identificeren en beheersen om onbedoeld gebruik of levering te "
            "voorkomen. Afwijkingen moeten worden gedocumenteerd."
        ),
        "interpretatie": (
            "Niet-conformiteiten moeten worden gevonden vóórdat ze de klant "
            "bereiken. Goede non-conformiteitsbeheer geeft ook waardevolle "
            "data voor verbeterinitiatieven. De auditor controleert of "
            "afwijkingen consequent worden vastgelegd en afgehandeld."
        ),
        "bewijslast": [
            "Non-conformiteitenprocedure",
            "Non-conformiteitenregister of NCR-formulieren",
            "Bewijs van correctieve maatregelen bij herhaalde afwijkingen",
            "Klantcommunicatie bij afwijkend geleverd product",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Non-conforme outputs geïdentificeerd en onder controle gebracht (gebruik/levering voorkomen)",
                "bewijslast": [
                    "Non-conformiteitenregister of bug tracker met status (geblokkeerd/terug naar dev)",
                ],
            },
            {
                "id": "b",
                "eis": "Actie genomen: correctie, retentie, retour of uitzonderingsgodkeuring",
                "bewijslast": [
                    "NCR of incident record met beschrijving actie en uitkomst",
                ],
            },
            {
                "id": "c",
                "eis": "Klant of bevoegde autoriteit geïnformeerd indien non-conform product/dienst geleverd",
                "bewijslast": [
                    "Communicatierecord bij afwijkende levering (e-mail, ticket, notitie klantoverleg)",
                ],
            },
            {
                "id": "d",
                "eis": "Gedocumenteerde informatie als bewijs: beschrijving afwijking, acties en eventuele uitzonderingstoestemming",
                "bewijslast": [
                    "Compleet NCR-formulier of gestructureerd incident-ticket met alle vereiste velden",
                ],
            },
        ],
    },
    "9.1": {
        "normtekst": (
            "De organisatie moet bepalen wat, hoe en wanneer wordt gemonitord, "
            "gemeten, geanalyseerd en beoordeeld. Zij moet de prestaties en de "
            "effectiviteit van het kwaliteitsmanagementsysteem evalueren."
        ),
        "interpretatie": (
            "Meten zonder analyseren is zinloos. Je moet bewuste keuzes maken "
            "over welke indicatoren iets zeggen over proceskwaliteit en "
            "klanttevredenheid. Klanttevredenheid meten is expliciet vereist, "
            "de methode mag je zelf kiezen."
        ),
        "bewijslast": [
            "KPI-overzicht met meetmethode en frequentie",
            "Klanttevredenheidsmetingen (enquête, NPS, klachtentrend)",
            "Analyse- en beoordelingsrapportages",
            "Bewijs van opvolging van analyseresultaten",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Bepaald: wat, hoe en wanneer gemonitord/gemeten wordt (processen, producten, KMS)",
                "bewijslast": [
                    "KPI-overzicht of monitoringsplan met meetmethode, frequentie en eigenaar",
                ],
            },
            {
                "id": "b",
                "eis": "Klanttevredenheid gemeten (methode naar eigen keuze: NPS, enquête, klachtentrend)",
                "bewijslast": [
                    "Klanttevredenheidsresultaten, NPS-score of klachtenanalyse met datum",
                ],
            },
            {
                "id": "c",
                "eis": "Data geanalyseerd en geëvalueerd; resultaten input voor directiebeoordeling",
                "bewijslast": [
                    "Analyse-rapportage of KPI-dashboard als input directiebeoordeling",
                ],
            },
            {
                "id": "d",
                "eis": "Analyseresultaten leiden tot opvolging en aantoonbare verbeteracties",
                "bewijslast": [
                    "Verbeteracties of besluitenlijst gekoppeld aan monitoringuitkomsten",
                ],
            },
        ],
    },
    "9.2": {
        "normtekst": (
            "De organisatie moet op geplande tijdstippen interne audits uitvoeren "
            "om vast te stellen of het kwaliteitsmanagementsysteem voldoet aan "
            "de eisen en effectief is geïmplementeerd en onderhouden."
        ),
        "interpretatie": (
            "Interne audits zijn de zelfreflectie van het KMS. Ze zijn geen "
            "formaliteit maar een echt toetsinstrument. Een auditprogramma moet "
            "alle processen en clausules periodiek omvatten en resultaten moeten "
            "leiden tot opvolging."
        ),
        "bewijslast": [
            "Jaarlijks intern auditprogramma",
            "Auditplannen en auditverslagen",
            "Non-conformiteiten en verbeteracties voortkomend uit interne audits",
            "Bewijs van kwalificatie van interne auditoren",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Auditprogramma vastgesteld: frequentie, methoden, verantwoordelijkheden, rapportage",
                "bewijslast": [
                    "Jaarlijks auditprogramma met alle KMS-clausules en processen gedekt",
                ],
            },
            {
                "id": "b",
                "eis": "Auditors zijn competent en objectief (niet eigen werk auditen)",
                "bewijslast": [
                    "Kwalificatierecord interne auditor of gebruik externe auditor voor zelfevaluatie",
                ],
            },
            {
                "id": "c",
                "eis": "Auditbevindingen gerapporteerd aan verantwoordelijk management",
                "bewijslast": [
                    "Auditverslag of auditrapport gericht aan directie/proceseigenaar",
                ],
            },
            {
                "id": "d",
                "eis": "Correcties en verbeteracties tijdig doorgevoerd na bevindingen",
                "bewijslast": [
                    "Actieoverzicht uit interne audits met status en afdoening",
                ],
            },
        ],
    },
    "9.3": {
        "normtekst": (
            "Het topmanagement moet het kwaliteitsmanagementsysteem op geplande "
            "tijdstippen beoordelen om te waarborgen dat het passend, adequaat "
            "en effectief blijft. De beoordeling moet specifieke inputs bevatten "
            "en outputs produceren."
        ),
        "interpretatie": (
            "De directiebeoordeling is het moment waarop de directie formeel "
            "verantwoordelijkheid neemt voor het KMS. Het is geen standaard "
            "vergadering: er zijn verplichte agenda-items en de uitkomsten "
            "moeten leiden tot concrete besluiten over middelen en verbetering."
        ),
        "bewijslast": [
            "Notulen directiebeoordeling (met alle verplichte inputs)",
            "Besluitenlijst met acties, eigenaren en termijnen",
            "Bewijs van opvolging van acties uit vorige directiebeoordeling",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Inputs aanwezig: status vorige review, veranderingen, prestaties, resources, risico's, verbetermogelijkheden",
                "bewijslast": [
                    "Directiebeoordeling-agenda met alle verplichte ISO 9001 §9.3.2 input-items",
                ],
            },
            {
                "id": "b",
                "eis": "Outputs zijn besluiten: verbeteringen, resource-behoeften, KMS-wijzigingen",
                "bewijslast": [
                    "Besluitenlijst uit directiebeoordeling met eigenaar en deadline per actie",
                ],
            },
            {
                "id": "c",
                "eis": "Acties uit vorige directiebeoordeling zijn opgevolgd en afgerond",
                "bewijslast": [
                    "Status-overzicht acties vorige review: open/gesloten/verschoven met motivatie",
                ],
            },
        ],
    },
    "10.1": {
        "normtekst": (
            "De organisatie moet kansen voor verbetering bepalen en selecteren "
            "en de nodige acties implementeren om aan klanteisen te voldoen en "
            "de klanttevredenheid te verhogen."
        ),
        "interpretatie": (
            "Verbetering is geen toevallige activiteit maar een systematische "
            "verplichting. De norm vraagt om bewuste keuzes over waar je "
            "investeert in verbetering, onderbouwd door data uit monitoring en "
            "analyse."
        ),
        "bewijslast": [
            "Verbeterregister of verbeterplannen",
            "Koppeling van verbeteracties aan data (klachten, audits, KPI's)",
            "Bewijs van implementatie en effectiviteitstoetsing van verbeteringen",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Verbetermogelijkheden bepaald op basis van data (klachten, KPI's, audits)",
                "bewijslast": [
                    "Verbeterregister of backlog met bron (klacht, audit, klanttevredenheid)",
                ],
            },
            {
                "id": "b",
                "eis": "Verbeteracties geïmplementeerd om aan klanteisen te voldoen en tevredenheid te verhogen",
                "bewijslast": [
                    "Bewijs van uitgevoerde verbeteringen en gemeten effect op klantervaring",
                ],
            },
        ],
    },
    "10.2": {
        "normtekst": (
            "Bij het optreden van een non-conformiteit moet de organisatie "
            "reageren, de oorzaak bepalen, beoordelen of vergelijkbare situaties "
            "bestaan en correctieve maatregelen nemen. Effectiviteit moet worden "
            "beoordeeld en gedocumenteerde informatie bewaard."
        ),
        "interpretatie": (
            "Correctieve maatregelen gaan over het wegnemen van oorzaken, niet "
            "alleen het oplossen van het symptoom. Een goede oorzaakanalyse "
            "(5x waarom, visgraatdiagram) is het bewijs dat je serieus omgaat "
            "met non-conformiteiten."
        ),
        "bewijslast": [
            "Correctieve-maatregelenprocedure",
            "NCR's met oorzaakanalyse en corrigerende maatregel",
            "Bewijs van effectiviteitscontrole na implementatie maatregel",
            "Geactualiseerd risicoregister op basis van non-conformiteiten",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Reactie op non-conformiteit: corrigeer het probleem en pak de gevolgen aan",
                "bewijslast": [
                    "NCR of incident-ticket met beschrijving actie en afdoening",
                ],
            },
            {
                "id": "b",
                "eis": "Oorzaakanalyse uitgevoerd om herhaling te voorkomen",
                "bewijslast": [
                    "Oorzaakanalyse (5×waarom, visgraat) opgenomen in NCR",
                ],
            },
            {
                "id": "c",
                "eis": "Beoordeling of vergelijkbare non-conformiteiten elders bestaan of kunnen ontstaan",
                "bewijslast": [
                    "Bewijs van scope-check: zijn vergelijkbare processen/projecten beoordeeld?",
                ],
            },
            {
                "id": "d",
                "eis": "Maatregel geïmplementeerd en effectiviteit beoordeeld; KMS bijgewerkt waar nodig",
                "bewijslast": [
                    "Effectiviteitscontrole in NCR of audit-bevinding met bewijs van afdoening",
                ],
            },
        ],
    },
    "10.3": {
        "normtekst": (
            "De organisatie moet de geschiktheid, adequaatheid en effectiviteit "
            "van het kwaliteitsmanagementsysteem continu verbeteren. Zij moet "
            "resultaten van analyse en beoordeling gebruiken om verbetermogelijkheden "
            "te bepalen."
        ),
        "interpretatie": (
            "Continue verbetering (kaizen-gedachte) is de overkoepelende "
            "ambitie van ISO 9001. Het gaat niet alleen om het herstellen van "
            "fouten, maar om het proactief verbeteren van prestaties. De "
            "PDCA-cyclus is hiervoor het raamwerk."
        ),
        "bewijslast": [
            "Aantoonbare trend in KPI-verbetering over meerdere periodes",
            "Verbeterinitiatieven voortkomend uit directiebeoordeling",
            "Bewijs van PDCA-cyclus toepassing in minimaal één verbeterproject",
        ],
        "sub_punten": [
            {
                "id": "a",
                "eis": "Geschiktheid, adequaatheid en effectiviteit KMS worden actief verbeterd",
                "bewijslast": [
                    "Verbeterregister of verbeterindicatoren met aantoonbare trend over tijd",
                ],
            },
            {
                "id": "b",
                "eis": "Uitkomsten van analyse, directiebeoordeling en audits worden gebruikt als verbeterinput",
                "bewijslast": [
                    "Koppeling: directiebeoordeling-output → verbeteractie in verbeterregister",
                ],
            },
            {
                "id": "c",
                "eis": "Continue verbetering is aantoonbaar (niet incidenteel, maar structureel geborgd)",
                "bewijslast": [
                    "Bewijs van PDCA-cyclus in minimaal één verbeterproject (plan, do, check, act)",
                ],
            },
        ],
    },
}


NORMTEKSTEN_27001 = {
    # ---- Organisatorische beheersmaatregelen (5.x) ----
    "5.1": {
        "normtekst": (
            "Beleid voor informatiebeveiliging en themaspecifieke beleidslijnen "
            "moeten worden vastgesteld, goedgekeurd door de directie, "
            "gepubliceerd, gecommuniceerd aan medewerkers en relevante "
            "belanghebbenden, en op geplande tijdstippen worden beoordeeld."
        ),
        "interpretatie": (
            "Zonder een duidelijk beleid weet niemand wat de spelregels zijn "
            "op het gebied van informatiebeveiliging. Het beleid geeft richting "
            "aan alle andere maatregelen. Een beleid dat alleen in een la ligt "
            "telt niet; het moet bekend en actueel zijn."
        ),
        "bewijslast": [
            "Informatiebeveiligingsbeleid ondertekend door directie",
            "Themaspecifieke beleidslijnen (toegang, cryptografie, BYOD, etc.)",
            "Bewijs van communicatie (intranet, onboarding, e-mail)",
            "Versiehistorie en datum laatste beoordeling",
        ],
    },
    "5.2": {
        "normtekst": (
            "Rollen en verantwoordelijkheden voor informatiebeveiliging moeten "
            "worden gedefinieerd en toegewezen overeenkomstig de behoeften van "
            "de organisatie."
        ),
        "interpretatie": (
            "Als niemand specifiek verantwoordelijk is voor beveiliging, is "
            "iedereen het in theorie maar niemand in de praktijk. Duidelijke "
            "rollen (CISO, data-eigenaar, systeembeheerder) voorkomen gaten in "
            "de beveiliging."
        ),
        "bewijslast": [
            "Organogram met informatiebeveiligingsrollen",
            "Functiebeschrijvingen met beveiligingsverantwoordelijkheden",
            "Benoemingsbesluit CISO of equivalent",
        ],
    },
    "5.3": {
        "normtekst": (
            "Conflicterende taken en conflicterende verantwoordelijkheden moeten "
            "worden gescheiden om de kans op ongeautoriseerde of onbedoelde "
            "wijziging of misbruik van activa van de organisatie te verkleinen."
        ),
        "interpretatie": (
            "Functiescheiding (segregation of duties) voorkomt dat één persoon "
            "fraude kan plegen of fouten kan verbergen. Denk aan het scheiden "
            "van aanvragen, goedkeuren en uitvoeren van toegangsrechten of "
            "financiële transacties."
        ),
        "bewijslast": [
            "Functiescheidingsmatrix of SOD-analyse",
            "Bewijs dat kritieke processtappen door verschillende personen worden uitgevoerd",
            "Compenserende maatregelen waar volledige scheiding niet mogelijk is",
        ],
    },
    "5.4": {
        "normtekst": (
            "Het management moet van alle medewerkers verlangen dat zij "
            "informatiebeveiliging toepassen in overeenstemming met het beleid "
            "en de procedures van de organisatie."
        ),
        "interpretatie": (
            "Beveiliging is niet alleen een IT-verantwoordelijkheid. Het "
            "management moet actief uitdragen en afdwingen dat medewerkers "
            "zich aan beveiligingsregels houden. Dit vraagt om duidelijke "
            "verwachtingen en consequenties bij niet-naleving."
        ),
        "bewijslast": [
            "Arbeidsovereenkomst of gedragscode met beveiligingsverplichtingen",
            "Bewijs van managementcommunicatie over beveiligingsverwachtingen",
            "Disciplinaire procedure bij schending beveiligingsbeleid",
        ],
    },
    "5.5": {
        "normtekst": (
            "De organisatie moet contacten onderhouden met relevante overheids- "
            "en regelgevende autoriteiten op het gebied van informatiebeveiliging."
        ),
        "interpretatie": (
            "Bij een incident of datalek moet je weten wie je moet bellen: "
            "de AP, het NCSC, of sectorale toezichthouders. Het gaat erom "
            "dat deze contacten vooraf zijn vastgelegd, niet dat je ze pas "
            "zoekt als het te laat is."
        ),
        "bewijslast": [
            "Contactenlijst relevante autoriteiten (AP, NCSC, sectortoezichthouder)",
            "Procedure voor melding datalekken met contactgegevens",
            "Bewijs van periodiek contact of deelname aan informatiedeling",
        ],
    },
    "5.6": {
        "normtekst": (
            "De organisatie moet contacten onderhouden met speciale "
            "belangengroepen, beveiligingsforums en professionele verenigingen "
            "op het gebied van informatiebeveiliging."
        ),
        "interpretatie": (
            "Dreigingen en kwetsbaarheden ontwikkelen zich snel. Door deel te "
            "nemen aan communities (ISAC's, NCSC-meldkringen, vakverenigingen) "
            "blijf je op de hoogte van relevante ontwikkelingen voordat ze je "
            "treffen."
        ),
        "bewijslast": [
            "Lijst van lidmaatschappen of abonnementen op dreigingsinformatie",
            "Bewijs van deelname aan sector-ISAC of vergelijkbaar netwerk",
            "Procedure voor verwerking van ontvangen dreigingsinformatie",
        ],
    },
    "5.7": {
        "normtekst": (
            "Informatie over informatiebeveiligingsdreigingen moet worden "
            "verzameld en geanalyseerd om dreigingsinformatie te produceren die "
            "kan worden gebruikt om beveiligingsbeslissingen te ondersteunen."
        ),
        "interpretatie": (
            "Threat intelligence is meer dan het lezen van nieuwsberichten. "
            "Je moet actief informatie verzamelen over relevante dreigingen, "
            "deze analyseren op relevantie voor jouw context en er "
            "beslissingen op baseren over maatregelen."
        ),
        "bewijslast": [
            "Threat intelligence bronnen en abonnementen",
            "Proces voor analyse en verwerking van dreigingsinformatie",
            "Bewijs van aanpassing van maatregelen op basis van threat intel",
        ],
    },
    "5.8": {
        "normtekst": (
            "Informatiebeveiliging moet worden geïntegreerd in projectmanagement "
            "zodat informatiebeveiligingsrisico's worden geïdentificeerd en "
            "aangepakt als onderdeel van projecten."
        ),
        "interpretatie": (
            "Beveiliging achteraf inbouwen is duurder en minder effectief dan "
            "security by design. Door beveiliging in projectgateway's op te "
            "nemen voorkom je dat nieuwe systemen en processen gaten in je "
            "beveiligingslandschap creëren."
        ),
        "bewijslast": [
            "Projectmethodologie met beveiligingscheckpoints",
            "Privacy/security impact assessment (PIA/DPIA) voor projecten",
            "Bewijs van beveiligingsbeoordeling bij oplevering projecten",
        ],
    },
    "5.9": {
        "normtekst": (
            "Een inventaris van informatie en andere daarmee samenhangende "
            "activa, inclusief eigenaren, moet worden opgesteld en onderhouden."
        ),
        "interpretatie": (
            "Je kunt geen activa beschermen die je niet kent. Een bijgewerkt "
            "activa-register is de basis voor risicoanalyse, classificatie en "
            "beveiligingsmaatregelen. Activa zonder eigenaar worden stelselmatig "
            "verwaarloosd."
        ),
        "bewijslast": [
            "Informatieactiva-register met eigenaar per actief",
            "Procedure voor registratie van nieuwe activa",
            "Bewijs van periodieke actualisatie van het register",
        ],
    },
    "5.10": {
        "normtekst": (
            "Regels voor acceptabel gebruik en procedures voor de omgang met "
            "informatie en andere daarmee samenhangende activa moeten worden "
            "geïdentificeerd, gedocumenteerd en geïmplementeerd."
        ),
        "interpretatie": (
            "Medewerkers moeten weten wat wel en niet mag met bedrijfsinformatie "
            "en -apparatuur. Onduidelijkheid leidt tot risicovol gedrag zonder "
            "kwade wil. Acceptabel gebruiksbeleid stelt duidelijke grenzen."
        ),
        "bewijslast": [
            "Acceptable use policy (AUP) voor informatiesystemen",
            "Bewijs van communicatie en acceptatie door medewerkers",
            "Specifieke regels voor mobiele apparaten, cloud en sociale media",
        ],
    },
    "5.11": {
        "normtekst": (
            "Procedures voor de teruggave of vernietiging van informatie en "
            "andere daarmee samenhangende activa bij beëindiging of wijziging "
            "van het dienstverband of contract moeten worden gedefinieerd en "
            "geïmplementeerd."
        ),
        "interpretatie": (
            "Als medewerkers of leveranciers vertrekken, moeten toegangsrechten "
            "worden ingetrokken en bedrijfsmiddelen worden teruggegeven. Dit "
            "is een kritiek moment dat geregeld gedrag vereist, niet "
            "improvisatie."
        ),
        "bewijslast": [
            "Offboarding-checklist voor medewerkers en contractanten",
            "Bewijs van tijdige intrekking van toegangsrechten bij uitdiensttreding",
            "Records van teruggave of vernietiging van activa",
        ],
    },
    "5.12": {
        "normtekst": (
            "Informatie moet worden geclassificeerd op basis van de "
            "informatiebeveiligingsbehoeften van de organisatie, rekening "
            "houdend met vertrouwelijkheid, integriteit en beschikbaarheid."
        ),
        "interpretatie": (
            "Niet alle informatie is even gevoelig. Door te classificeren "
            "(bijv. openbaar, intern, vertrouwelijk, geheim) kun je "
            "proportionele maatregelen treffen. Zonder classificatie "
            "behandel je alles hetzelfde, wat inefficiënt en onveilig is."
        ),
        "bewijslast": [
            "Informatieclassificatiebeleid met classificatieniveaus",
            "Classificatieschema toegepast op activa-register",
            "Bewijs van gebruik van classificatielabels op documenten",
        ],
    },
    "5.13": {
        "normtekst": (
            "Een passende set procedures voor labeling van informatie moet worden "
            "ontwikkeld en geïmplementeerd in overeenstemming met het "
            "informatieclassificatieschema."
        ),
        "interpretatie": (
            "Classificatie heeft alleen waarde als informatie ook daadwerkelijk "
            "wordt gelabeld. Labels op documenten, e-mails en systemen maken "
            "het voor medewerkers eenvoudig om te weten hoe ze informatie "
            "moeten behandelen."
        ),
        "bewijslast": [
            "Labelingsprocedure per classificatieniveau",
            "Bewijs van labelgebruik (voorbeelddocumenten, e-mailheaders)",
            "Technische implementatie van labels (DLP, Azure Information Protection)",
        ],
    },
    "5.14": {
        "normtekst": (
            "Regels voor informatieoverdracht moeten worden gedefinieerd voor "
            "alle soorten overdrachtsvoorzieningen en moeten overeenkomsten "
            "voor informatieoverdracht omvatten voor externe partijen."
        ),
        "interpretatie": (
            "Informatieoverdracht via e-mail, FTP, USB of fysieke post draagt "
            "beveiligingsrisico's. Door hiervoor expliciete regels te stellen "
            "en afspraken met externe partijen te maken, reduceer je de kans "
            "op datalekken bij overdracht."
        ),
        "bewijslast": [
            "Beleid voor informatieoverdracht (intern en extern)",
            "Non-disclosure agreements (NDA's) met externe partijen",
            "Technische maatregelen voor veilige overdracht (encryptie, VPN)",
        ],
    },
    "5.15": {
        "normtekst": (
            "Regels voor toegangsbeheersing tot informatie en andere "
            "daarmee samenhangende activa moeten worden vastgesteld en "
            "geïmplementeerd op basis van bedrijfs- en "
            "informatiebeveiligingseisen."
        ),
        "interpretatie": (
            "Toegangsbeheersing is de kern van informatiebeveiliging: alleen "
            "de juiste personen hebben toegang tot de juiste informatie op het "
            "juiste moment. Het beleid stelt de regels; technische maatregelen "
            "en processen voeren ze uit."
        ),
        "bewijslast": [
            "Toegangsbeheersingsbeleid",
            "Rolgebaseerde toegangsmatrix (RBAC)",
            "Procedure voor aanvraag, goedkeuring en intrekking van toegangsrechten",
        ],
    },
    "5.16": {
        "normtekst": (
            "De volledige levenscyclus van identiteiten moet worden beheerd "
            "in overeenstemming met het toegangsbeheersingsbeleid."
        ),
        "interpretatie": (
            "Identiteitsbeheer gaat over het aanmaken, wijzigen en verwijderen "
            "van accounts. Slapende accounts van ex-medewerkers zijn een "
            "veelvoorkomend beveiligingsrisico. Geautomatiseerd identiteitsbeheer "
            "vermindert handmatige fouten."
        ),
        "bewijslast": [
            "Identity lifecycle management procedure",
            "Bewijs van tijdige deactivering accounts bij uitdiensttreding",
            "Periodieke toegangsreview (user access review) resultaten",
        ],
    },
    "5.17": {
        "normtekst": (
            "Beheer van authenticatie-informatie moet worden beheerst door middel "
            "van een formeel beheersproces, inclusief advies aan gebruikers over "
            "het omgaan met authenticatie-informatie."
        ),
        "interpretatie": (
            "Wachtwoorden en andere authenticatiegegevens zijn de sleutels tot "
            "systemen. Zwak wachtwoordbeleid, gedeelde accounts of onversleutelde "
            "opslag zijn directe risico's. MFA is inmiddels de norm voor "
            "kritieke systemen."
        ),
        "bewijslast": [
            "Wachtwoordbeleid met complexiteits- en verloopvereisten",
            "Bewijs van MFA-implementatie op kritieke systemen",
            "Procedure voor beheer van privileged accounts en service-accounts",
        ],
    },
    "5.18": {
        "normtekst": (
            "Toegangsrechten tot informatie en andere daarmee samenhangende "
            "activa moeten worden verstrekt, beoordeeld, gewijzigd en "
            "ingetrokken overeenkomstig het themaspecifieke beleid en de "
            "regels van de organisatie."
        ),
        "interpretatie": (
            "Toegangsrechten slijten: functies veranderen, projecten eindigen, "
            "mensen vertrekken. Periodieke review van toegangsrechten (access "
            "recertification) zorgt ervoor dat alleen actuele rechten actief zijn "
            "en voorkomt privilege creep."
        ),
        "bewijslast": [
            "Procedure voor toekenning en intrekking van toegangsrechten",
            "Records van toegangsreviews (halfjaarlijks of jaarlijks)",
            "Bewijs van prompte intrekking bij functiewijziging of vertrek",
        ],
    },
    "5.19": {
        "normtekst": (
            "Processen en procedures moeten worden gedefinieerd en "
            "geïmplementeerd om de informatiebeveiligingsrisico's die verband "
            "houden met het gebruik van producten of diensten van leveranciers "
            "te beheersen."
        ),
        "interpretatie": (
            "Leveranciers en dienstverleners hebben toegang tot systemen en "
            "data. Als zij niet dezelfde beveiligingsnorm hanteren als jij, "
            "ontstaan kwetsbaarheden buiten je directe controle. "
            "Leveranciersrisicobeheer is essentieel in een uitbestede omgeving."
        ),
        "bewijslast": [
            "Leveranciersbeveiligingsbeleid",
            "Risicobeoordelingsproces voor leveranciers",
            "Contractuele beveiligingsvereisten voor leveranciers",
        ],
    },
    "5.20": {
        "normtekst": (
            "Informatiebeveiligingseisen moeten worden vastgesteld en "
            "overeengekomen met elke leverancier op basis van het type "
            "leveranciersrelatie en het risiconiveau."
        ),
        "interpretatie": (
            "Het is niet voldoende om intern beveiligingseisen te hebben; "
            "leveranciers moeten deze contractueel accepteren. SLA's en "
            "contracten moeten beveiligingsvereisten bevatten die "
            "afdwingbaar zijn."
        ),
        "bewijslast": [
            "Standaard beveiligingsbijlage bij leverancierscontracten",
            "Getekende verwerkersovereenkomsten (AVG-verplichting)",
            "Bewijs van beveiligingseisen in offertetraject (RFP/RFI)",
        ],
    },
    "5.21": {
        "normtekst": (
            "Procedures en eisen voor het beheer van informatiebeveiligingsrisico's "
            "in verband met de ICT-toeleveringsketen moeten worden vastgesteld "
            "en geïmplementeerd."
        ),
        "interpretatie": (
            "De toeleveringsketen voor software en hardware bevat risico's die "
            "je niet direct controleert (SolarWinds, XZ-utils). Je moet weten "
            "welke componenten je gebruikt en nadenken over risico's van "
            "gecompromitteerde toeleveranciers."
        ),
        "bewijslast": [
            "Software Bill of Materials (SBOM) of componentenregister",
            "Procedure voor beoordeling van ICT-toeleveranciers",
            "Bewijs van monitoring op kwetsbaarheden in gebruikte componenten",
        ],
    },
    "5.22": {
        "normtekst": (
            "De organisatie moet regelmatig de informatiebeveiligingspraktijken "
            "en dienstverlening van leveranciers monitoren, beoordelen, evalueren "
            "en wijzigingen beheren."
        ),
        "interpretatie": (
            "Leveranciersbeheer stopt niet bij contractondertekening. Periodieke "
            "reviews van leveranciersprestaties en beveiligingsnaleving zorgen "
            "ervoor dat afspraken ook daadwerkelijk worden nagekomen en dat je "
            "veranderingen tijdig signaleert."
        ),
        "bewijslast": [
            "Leveranciersbeoordelingsrapportages",
            "Bewijs van periodieke beveiligingsreviews met leveranciers",
            "Proces voor beheer van leverancierswijzigingen (wijzigingsbeheer)",
        ],
    },
    "5.23": {
        "normtekst": (
            "Processen voor het verwerven, gebruiken, beheren en beëindigen van "
            "informatiebeveiligingsdiensten in de cloud moeten worden vastgesteld "
            "overeenkomstig de informatiebeveiligingseisen van de organisatie."
        ),
        "interpretatie": (
            "Cloud introduceert specifieke risico's rondom dataresidenentie, "
            "gedeelde verantwoordelijkheid (shared responsibility model) en "
            "lock-in. Je moet expliciete afspraken maken met cloudproviders "
            "en weten wie verantwoordelijk is voor welk beveiligingsaspect."
        ),
        "bewijslast": [
            "Cloud security beleid en shared responsibility matrix",
            "Contractuele beveiligingsafspraken met cloudproviders",
            "Bewijs van configuratiebeheer cloudomgevingen (CIS benchmarks)",
        ],
    },
    "5.24": {
        "normtekst": (
            "De organisatie moet plannen en zich voorbereiden op het beheren van "
            "informatiebeveiligingsincidenten door rollen, verantwoordelijkheden "
            "en procedures te definiëren voor incidentrespons."
        ),
        "interpretatie": (
            "Improviseren tijdens een beveiligingsincident is kostbaar. "
            "Een vooraf gedefinieerd incidentresponsplan zorgt voor een "
            "gecontroleerde aanpak, snellere herstel en minder schade. "
            "Rollen moeten vooraf zijn belegd, niet pas bij een incident."
        ),
        "bewijslast": [
            "Informatiebeveiligingsincident respons procedure",
            "RACI voor incidentresponsteam",
            "Bewijs van oefening of test van het incidentresponsplan",
        ],
    },
    "5.25": {
        "normtekst": (
            "De organisatie moet informatiebeveiligingsgebeurtenissen beoordelen "
            "en beslissen of ze als informatiebeveiligingsincidenten moeten worden "
            "geclassificeerd."
        ),
        "interpretatie": (
            "Niet elke beveiligingsgebeurtenis is een incident. Door een heldere "
            "classificatieprocedure te hebben voorkom je zowel overreactie als "
            "onderrapportage. De drempel voor melding moet laag zijn; "
            "de drempel voor escalatie proportioneel."
        ),
        "bewijslast": [
            "Incidentclassificatieschema of -criteria",
            "Incidentenregister met classificatierecords",
            "Bewijs van triageprocedure voor beveiligingsgebeurtenissen",
        ],
    },
    "5.26": {
        "normtekst": (
            "Op informatiebeveiligingsincidenten moet worden gereageerd "
            "overeenkomstig de gedocumenteerde procedures."
        ),
        "interpretatie": (
            "Bij een incident telt elke minuut. Procedures moeten de "
            "response structureren: insluiting, onderzoek, herstel en "
            "communicatie. Na afloop moet een lessons-learned plaatsvinden "
            "om herhaling te voorkomen."
        ),
        "bewijslast": [
            "Incidentresponslogboek of ticketregistratie",
            "Bewijs van uitgevoerde respons conform procedure",
            "Post-incident review verslagen (lessons learned)",
        ],
    },
    "5.27": {
        "normtekst": (
            "Kennis opgedaan uit informatiebeveiligingsincidenten moet worden "
            "gebruikt om de kans op of gevolgen van toekomstige incidenten te "
            "verkleinen."
        ),
        "interpretatie": (
            "Elk incident is een leerkans. Structurele analyse van incidenten "
            "levert inzichten die preventieve maatregelen rechtvaardigen. "
            "Organisaties die hier geen gebruik van maken, lopen dezelfde "
            "incidenten steeds opnieuw op."
        ),
        "bewijslast": [
            "Post-incident review verslagen",
            "Bewijs van implementatie van verbeteringen na incidenten",
            "Trendanalyse incidentenregister (periodiek)",
        ],
    },
    "5.28": {
        "normtekst": (
            "De organisatie moet procedures vaststellen voor de identificatie, "
            "verzameling, verwerving en bewaring van bewijsmateriaal dat "
            "gerelateerd is aan informatiebeveiligingsincidenten."
        ),
        "interpretatie": (
            "Digitaal bewijsmateriaal kan nodig zijn voor disciplinaire "
            "procedures, rechtszaken of forensisch onderzoek. Als bewijsverzameling "
            "niet forensisch correct verloopt, is het bewijs onbruikbaar. "
            "Forensische procedures moeten van tevoren zijn vastgesteld."
        ),
        "bewijslast": [
            "Digitale forensics procedure (chain of custody)",
            "Bewijs van logging en log-retentiebeleid",
            "Procedure voor bewaring van forensisch bewijsmateriaal",
        ],
    },
    "5.29": {
        "normtekst": (
            "De organisatie moet plannen en maatregelen implementeren voor het "
            "handhaven van informatiebeveiliging tijdens verstoring."
        ),
        "interpretatie": (
            "Bij een calamiteit (brand, DDoS, uitval leverancier) staan "
            "informatiebeveiliging en bedrijfscontinuïteit op gespannen voet. "
            "Beveiliging mag niet worden opgeofferd voor snelheid van herstel. "
            "Continuïteitsplannen moeten beveiligingsvereisten integreren."
        ),
        "bewijslast": [
            "Business continuity plan met beveiligingsparagraaf",
            "Bewijs van integratie van beveiligingseisen in herstelplannen",
            "BCP-oefenverslagen inclusief beveiligingsaspecten",
        ],
    },
    "5.30": {
        "normtekst": (
            "ICT-gereedheid moet worden gepland, geïmplementeerd, onderhouden "
            "en getest op basis van bedrijfscontinuïteitsdoelstellingen en "
            "ICT-continuïteitseisen."
        ),
        "interpretatie": (
            "ICT-continuïteit gaat over het kunnen herstellen van systemen "
            "binnen de gestelde RTO en RPO. Dit vereist technische maatregelen "
            "(back-ups, redundantie) én procedures én regelmatig testen. "
            "Ongeteste continuïteitsplannen zijn geen plannen maar wensen."
        ),
        "bewijslast": [
            "ICT-continuïteitsplan met RTO/RPO per systeem",
            "Back-upbeleid en back-uptestresultaten",
            "DR-oefenverslagen (disaster recovery tests)",
        ],
    },
    "5.31": {
        "normtekst": (
            "Wettelijke, statutaire, regelgevende en contractuele eisen die "
            "relevant zijn voor informatiebeveiliging moeten worden "
            "geïdentificeerd, gedocumenteerd en actueel gehouden."
        ),
        "interpretatie": (
            "AVG, NIS2, sectorale wetgeving en contractuele verplichtingen "
            "creëren beveiligingseisen die je niet kunt negeren. Door een "
            "actueel register te onderhouden weet je wat je moet naleven en "
            "kun je aantonen dat je dit ook doet."
        ),
        "bewijslast": [
            "Wettelijk en regelgevend complianceregister",
            "Bewijs van periodieke beoordeling op nieuwe wet- en regelgeving",
            "Koppeling tussen wettelijke eisen en geïmplementeerde maatregelen",
        ],
    },
    "5.32": {
        "normtekst": (
            "De organisatie moet procedures implementeren om intellectuele "
            "eigendomsrechten te beschermen en het gebruik van propriëtaire "
            "software te beheren."
        ),
        "interpretatie": (
            "Illegaal software gebruik en schending van auteursrechten zijn "
            "juridische risico's. Softwarelicenties moeten worden bijgehouden "
            "en nageleefd. Open source software vereist begrip van licentie- "
            "voorwaarden (GPL, MIT, etc.)."
        ),
        "bewijslast": [
            "Software Asset Management (SAM) register",
            "Bewijs van naleving licentievoorwaarden",
            "Procedure voor gebruik van open source componenten",
        ],
    },
    "5.33": {
        "normtekst": (
            "Registraties moeten worden beschermd tegen verlies, vernietiging, "
            "vervalsing en onbevoegde toegang en vrijgave, overeenkomstig "
            "wettelijke, statutaire, regelgevende en contractuele eisen."
        ),
        "interpretatie": (
            "Bedrijfsregistraties (contracten, financiële records, auditrails) "
            "zijn juridisch en operationeel van groot belang. Goede bescherming "
            "en retentie zorgen dat records beschikbaar zijn wanneer nodig en "
            "vernietigd worden wanneer ze niet meer nodig zijn."
        ),
        "bewijslast": [
            "Retentiebeleid voor registraties met bewaartermijnen",
            "Bewijs van bescherming van kritieke registraties (toegangsbeheersing, back-up)",
            "Procedure voor veilige verwijdering na verloop retentietermijn",
        ],
    },
    "5.34": {
        "normtekst": (
            "De organisatie moet de privacy en bescherming van persoonsgegevens "
            "waarborgen zoals vereist door relevante wet- en regelgeving."
        ),
        "interpretatie": (
            "AVG-naleving is niet optioneel. Privacy moet worden ingebouwd in "
            "processen en systemen (privacy by design). De overlap tussen "
            "informatiebeveiliging en privacy is groot; goede samenwerking "
            "tussen CISO en FG is essentieel."
        ),
        "bewijslast": [
            "Privacybeleid en verwerkingsregister (AVG artikel 30)",
            "DPIA's voor risicovolle verwerkingen",
            "Bewijs van privacy by design bij nieuwe systemen",
        ],
    },
    "5.35": {
        "normtekst": (
            "Een onafhankelijke beoordeling van de aanpak van de organisatie "
            "voor het beheren van informatiebeveiliging en de implementatie "
            "ervan moet op geplande tijdstippen of bij significante wijzigingen "
            "worden uitgevoerd."
        ),
        "interpretatie": (
            "Interne beoordelingen hebben blinde vlekken. Een onafhankelijke "
            "review (interne audit door onafhankelijke partij, externe audit, "
            "of penetratietest) biedt een objectiever beeld van de volwassenheid "
            "van het ISMS."
        ),
        "bewijslast": [
            "Rapporten van onafhankelijke ISMS-beoordelingen",
            "Bewijs van opvolging van bevindingen",
            "Planning van periodieke onafhankelijke reviews",
        ],
    },
    "5.36": {
        "normtekst": (
            "Naleving van het informatiebeveiligingsbeleid, themaspecifieke "
            "beleidslijnen en technische normen van de organisatie moet "
            "regelmatig worden beoordeeld."
        ),
        "interpretatie": (
            "Beleid schrijven is stap één; handhaven is stap twee. Periodieke "
            "compliancereviews (technisch en procedureel) tonen aan dat beleid "
            "niet alleen op papier bestaat maar ook in de praktijk wordt "
            "nageleefd."
        ),
        "bewijslast": [
            "Compliancereview rapporten per beleidsdocument",
            "Technische compliancescans (vulnerability assessments, configuratiereviews)",
            "Bewijs van opvolging van non-compliant bevindingen",
        ],
    },
    "5.37": {
        "normtekst": (
            "Gedocumenteerde bedieningsprocedures voor informatie- "
            "verwerkingsfaciliteiten moeten beschikbaar worden gesteld aan "
            "alle gebruikers die deze nodig hebben."
        ),
        "interpretatie": (
            "Procedures voor het bedienen van systemen moeten beschikbaar en "
            "actueel zijn zodat systemen consistent en correct worden gebruikt. "
            "Dit geldt zowel voor reguliere operatie als voor noodsituaties."
        ),
        "bewijslast": [
            "Operationele procedures voor kritieke systemen",
            "Bewijs van beschikbaarheid voor relevante gebruikers",
            "Versiehistorie en goedkeuringsrecords van procedures",
        ],
    },
    # ---- Mensgerichte beheersmaatregelen (6.x) ----
    "6.1": {
        "normtekst": (
            "Achtergrondverificaties van alle kandidaten voor een dienstverband "
            "moeten worden uitgevoerd voordat zij toetreden tot de organisatie "
            "en op doorlopende basis, rekening houdend met wet- en regelgeving "
            "en ethische overwegingen."
        ),
        "interpretatie": (
            "Personeel is een van de grootste risicofactoren voor "
            "informatiebeveiliging. Screening voor indiensttreding verlaagt "
            "het risico op insider threats. De diepte van screening moet "
            "proportioneel zijn aan de gevoeligheid van de functie."
        ),
        "bewijslast": [
            "Screeningbeleid voor nieuwe medewerkers en contractanten",
            "Records van uitgevoerde screenings (VOG, referentiecheck)",
            "Procedure voor periodieke rescreening bij gevoelige functies",
        ],
    },
    "6.2": {
        "normtekst": (
            "Arbeidsovereenkomsten en contracten moeten de verantwoordelijkheden "
            "van de medewerkers en de organisatie voor informatiebeveiliging "
            "vastleggen."
        ),
        "interpretatie": (
            "Beveiligingsverplichtingen moeten contractueel zijn vastgelegd "
            "zodat ze afdwingbaar zijn. Medewerkers moeten begrijpen wat ze "
            "tekenen. Dit geldt ook voor contractanten en externe medewerkers."
        ),
        "bewijslast": [
            "Arbeidscontract met beveiligingsclausules",
            "Geheimhoudingsverklaringen (NDA's)",
            "Bewijs van acceptatie door medewerker",
        ],
    },
    "6.3": {
        "normtekst": (
            "Medewerkers en relevante contractanten moeten passend bewustzijn, "
            "onderwijs en opleiding ontvangen over informatiebeveiliging en "
            "regelmatige updates van het beleid."
        ),
        "interpretatie": (
            "Technische maatregelen falen als medewerkers niet begrijpen waarom "
            "beveiliging belangrijk is en hoe ze moeten handelen. Awareness "
            "training is de meest kosteneffectieve maatregel tegen social "
            "engineering en menselijke fouten."
        ),
        "bewijslast": [
            "Security awareness trainingsprogramma en -planning",
            "Trainingscompletierecords per medewerker",
            "Phishing simulatieresultaten en follow-up trainingen",
        ],
    },
    "6.4": {
        "normtekst": (
            "Er moet een formeel en gecommuniceerd disciplinair proces bestaan "
            "en worden geactiveerd om actie te ondernemen tegen medewerkers en "
            "andere relevante betrokken partijen die een informatiebeveiligings- "
            "overtreding begaan hebben."
        ),
        "interpretatie": (
            "Zonder consequenties voor beleidsovertredingen heeft beleid geen "
            "afschrikkende werking. Het disciplinaire proces moet eerlijk, "
            "proportioneel en vooraf bekend zijn. Dit werkt preventief en "
            "beschermt de organisatie juridisch."
        ),
        "bewijslast": [
            "Disciplinaire procedure met beveiligingsovertredingen",
            "Arbeidsreglement of gedragscode met sancties",
            "Bewijs van toepassing van procedure (geanonimiseerde cases)",
        ],
    },
    "6.5": {
        "normtekst": (
            "Informatiebeveiligingsverantwoordelijkheden en -verplichtingen die "
            "van kracht blijven na beëindiging of wijziging van het "
            "dienstverband moeten worden gedefinieerd, gecommuniceerd en "
            "gehandhaafd."
        ),
        "interpretatie": (
            "Geheimhouding eindigt niet op de laatste werkdag. Medewerkers "
            "moeten weten dat hun beveiligingsverplichtingen (NDA, "
            "geheimhouding) doorlopen na vertrek. Dit moet expliciet zijn "
            "vastgelegd in het contract."
        ),
        "bewijslast": [
            "Arbeidscontract met post-employment beveiligingsverplichtingen",
            "Exit-procedure met bevestiging van doorlopende verplichtingen",
            "NDA met expliciete doorlooptermijn na beëindiging dienstverband",
        ],
    },
    "6.6": {
        "normtekst": (
            "Informatiebeveiligingseisen moeten worden opgenomen in overeenkomsten "
            "met personeel en contractanten."
        ),
        "interpretatie": (
            "Externe medewerkers en ZZP'ers vormen net zo'n risico als vaste "
            "medewerkers, maar hebben vaak minder binding met de organisatie. "
            "Contractuele beveiligingseisen maken verwachtingen expliciet en "
            "afdwingbaar."
        ),
        "bewijslast": [
            "Standaard beveiligingsbijlage bij inhuurcontracten",
            "Getekende geheimhoudingsverklaringen voor contractanten",
            "Onboarding-checklist voor externe medewerkers met beveiligingsvereisten",
        ],
    },
    "6.7": {
        "normtekst": (
            "Maatregelen voor informatiebeveiliging moeten worden geïmplementeerd "
            "wanneer medewerkers op afstand werken om de informatie die buiten "
            "het terrein van de organisatie wordt benaderd, verwerkt of opgeslagen "
            "te beschermen."
        ),
        "interpretatie": (
            "Thuiswerken en onderweg werken vergroot het aanvalsoppervlak. "
            "Thuis-wifi, persoonlijke apparaten en gedeelde werkruimtes "
            "introduceren risico's die op kantoor niet bestaan. Remote work "
            "beleid moet deze risico's adresseren."
        ),
        "bewijslast": [
            "Remote work beveiligingsbeleid",
            "Technische maatregelen (VPN, MDM, versleutelde apparaten)",
            "Bewijs van communicatie van regels voor thuiswerken",
        ],
    },
    "6.8": {
        "normtekst": (
            "De organisatie moet een mechanisme bieden waarmee medewerkers "
            "waargenomen of vermoede informatiebeveiligingsgebeurtenissen "
            "kunnen rapporteren via passende kanalen."
        ),
        "interpretatie": (
            "Medewerkers zijn de eerste verdedigingslinie. Als het onduidelijk "
            "is hoe en waar je een verdacht incident meldt, worden veel "
            "incidenten nooit gemeld. Meldkanalen moeten laagdrempelig, "
            "bekend en veilig zijn."
        ),
        "bewijslast": [
            "Procedure voor melden van beveiligingsincidenten door medewerkers",
            "Bewijs van communicatie van meldkanalen (intranet, poster, onboarding)",
            "Registratie van ontvangen meldingen en opvolging",
        ],
    },
    # ---- Fysieke beheersmaatregelen (7.x) ----
    "7.1": {
        "normtekst": (
            "Beveiligde fysieke perimeters moeten worden gedefinieerd en gebruikt "
            "om gebieden die informatie en andere daarmee samenhangende activa "
            "bevatten te beschermen."
        ),
        "interpretatie": (
            "Fysieke beveiliging begint bij de buitendeur. Perimeters (hekken, "
            "deuren, toegangspassen) bepalen wie het gebouw, de serverruimte "
            "en gevoelige zones kan betreden. Meerdere beveiligingslagen "
            "(defense in depth) zijn de norm."
        ),
        "bewijslast": [
            "Plattegrond met beveiligingszones en toegangspunten",
            "Toegangsbeheersingsysteem (badlezers, sleutelregistratie)",
            "Procedure voor beheer van fysieke toegangsmiddelen",
        ],
    },
    "7.2": {
        "normtekst": (
            "Beveiligde zones moeten worden beschermd door passende "
            "toegangsbeheersmaatregelen en toegangspunten."
        ),
        "interpretatie": (
            "Niet iedereen hoeft overal te komen. Toegang tot serverruimtes, "
            "archieven en andere gevoelige zones moet worden beperkt tot "
            "geautoriseerde personen. Bezoekers moeten worden begeleid."
        ),
        "bewijslast": [
            "Toegangsrechtenmatrix voor fysieke zones",
            "Bezoekersregistratie en begeleidingsprocedure",
            "Bewijs van periodieke review van fysieke toegangsrechten",
        ],
    },
    "7.3": {
        "normtekst": (
            "Fysieke beveiligingsmaatregelen voor kantoren, ruimtes en "
            "faciliteiten moeten worden ontworpen en geïmplementeerd."
        ),
        "interpretatie": (
            "Kantoren bevatten gevoelige documenten, apparaten en gesprekken. "
            "Clean desk policy, vergrendelde kasten en privacyschermen zijn "
            "eenvoudige maar effectieve maatregelen. Sensitiviteit van het "
            "kantoor bepaalt de vereiste maatregelen."
        ),
        "bewijslast": [
            "Clean desk en clean screen policy",
            "Bewijs van beveiligde opslag voor gevoelige documenten (kluizen, afgesloten kasten)",
            "Bewijs van afdoende beveiliging vergaderruimtes voor vertrouwelijke gesprekken",
        ],
    },
    "7.4": {
        "normtekst": (
            "Fysieke locaties moeten continu worden gemonitord op onbevoegde "
            "fysieke toegang."
        ),
        "interpretatie": (
            "Monitoring detecteert indringers en onbevoegde toegang die "
            "preventieve maatregelen ontwijken. CCTV, alarmsystemen en "
            "toegangslogboeken vormen samen een detectielaag. Monitoring "
            "heeft alleen waarde als iemand ook reageert op alerts."
        ),
        "bewijslast": [
            "CCTV-systeem en retentiebeleid voor opnamen",
            "Alarmsysteem en respons procedure",
            "Toegangslogboeken en bewijs van periodieke review",
        ],
    },
    "7.5": {
        "normtekst": (
            "Bescherming tegen fysieke en omgevingsdreigingen, zoals "
            "natuurrampen en andere opzettelijke of onopzettelijke fysieke "
            "bedreigingen voor de infrastructuur, moet worden ontworpen en "
            "geïmplementeerd."
        ),
        "interpretatie": (
            "Brand, overstroming, stroomuitval en extreme temperaturen kunnen "
            "systemen vernietigen. Fysieke omgevingsmaatregelen (brandblusser, "
            "watermelding, UPS, airconditioning) beschermen de hardware. "
            "Risicolocaties vereisen extra aandacht."
        ),
        "bewijslast": [
            "Risicoanalyse fysieke omgevingsdreigingen",
            "Bewijs van aanwezigheid brandblussers, rookmelders en watermelders",
            "UPS/noodstroomvoorziening testresultaten",
            "Klimaatbeheersingssysteem en monitoringrecords",
        ],
    },
    "7.6": {
        "normtekst": (
            "Maatregelen voor beveiliging in beveiligde zones of zones met een "
            "hoog risico moeten worden ontworpen en toegepast."
        ),
        "interpretatie": (
            "Activiteiten in beveiligde zones (serverruimtes, datacenters) "
            "vereisen extra gedragsregels: geen eenzame aanwezigheid, logging "
            "van alle activiteiten, verbod op camera's of voedsel. Deze "
            "maatregelen reduceren insider threats."
        ),
        "bewijslast": [
            "Gedragsregels voor beveiligde zones",
            "Logboek van toegang en activiteiten in serverruimte",
            "Procedure voor duo-controle bij kritieke handelingen",
        ],
    },
    "7.7": {
        "normtekst": (
            "Medewerkers en externe partijen die gebruikmaken van of toegang "
            "hebben tot activa van de organisatie moeten een clean desk beleid "
            "voor papieren documenten en verwijderbare opslagmedia toepassen "
            "en een clean screen beleid voor informatiefaciliteiten."
        ),
        "interpretatie": (
            "Documenten en schermen die zichtbaar zijn voor onbevoegden zijn "
            "een eenvoudig te misbruiken informatiebron. Clean desk/screen "
            "beleid is een basismaatregel die weinig kost maar veel oplevert. "
            "Effectiviteit vereist naleving en controle."
        ),
        "bewijslast": [
            "Clean desk en clean screen policy",
            "Bewijs van communicatie en naleving (steekproefcontroles)",
            "Screensaver- en vergrendelbeleid technisch afgedwongen",
        ],
    },
    "7.8": {
        "normtekst": (
            "Apparatuur moet op geschikte locaties worden geplaatst en beschermd "
            "om de risico's van omgevingsdreigingen en -gevaren en de "
            "mogelijkheid van onbevoegde toegang te verminderen."
        ),
        "interpretatie": (
            "Servers in een overstroombare kelder of beeldschermen zichtbaar "
            "vanaf de straat zijn onnodige risico's. De plaatsing van apparatuur "
            "moet weloverwogen zijn. Bekabeling moet worden beschermd tegen "
            "afluisteren en beschadiging."
        ),
        "bewijslast": [
            "Locatieplan apparatuur met verantwoording beveiligingskeuzes",
            "Bewijs van bescherming bekabeling (kabelgoten, afscherming)",
            "Datacenterinrichtingsdocumentatie",
        ],
    },
    "7.9": {
        "normtekst": (
            "Activa buiten het terrein moeten worden beschermd. Het risiconiveau "
            "van activa buiten het terrein van de organisatie moet in acht worden "
            "genomen en passende maatregelen moeten worden toegepast."
        ),
        "interpretatie": (
            "Laptops, smartphones en USB-sticks worden meegenomen buiten "
            "het beveiligde kantoor. Diefstal of verlies is een reëel risico. "
            "Encryptie van apparaten en data is de meest effectieve maatregel "
            "voor assets buiten de deur."
        ),
        "bewijslast": [
            "Beleid voor gebruik van activa buiten het terrein",
            "Bewijs van versleuteling van mobiele apparaten",
            "Procedure voor melding en opvolging van verlies of diefstal",
        ],
    },
    "7.10": {
        "normtekst": (
            "Opslagmedia moeten worden beheerd gedurende hun levenscyclus van "
            "verwerving, gebruik, transport en verwijdering in overeenstemming "
            "met het classificatieschema en de behandelingseisen van de organisatie."
        ),
        "interpretatie": (
            "USB-sticks, harde schijven en back-uptapes bevatten gevoelige data "
            "die niet zomaar in de prullenbak mogen. Veilige verwijdering "
            "(wissen, degaussen, fysiek vernietigen) voorkomt datalekken. "
            "Transport van media vereist ook bescherming."
        ),
        "bewijslast": [
            "Mediabeheerprocedure (registratie, gebruik, transport, verwijdering)",
            "Records van veilige mediaverwijdering (certificaten van vernietiging)",
            "Bewijs van versleuteling van verwijderbare media",
        ],
    },
    "7.11": {
        "normtekst": (
            "Informatiefaciliteiten moeten worden beschermd tegen "
            "stroomonderbrekingen en andere storingen als gevolg van "
            "uitval van ondersteunende nutsvoorzieningen."
        ),
        "interpretatie": (
            "Stroomuitval kan leiden tot dataverlies, systeemschade en "
            "bedrijfsonderbreking. UPS-systemen, noodgeneratoren en "
            "meervoudige stroomtoevoer zijn standaard maatregelen voor "
            "kritieke informatiesystemen."
        ),
        "bewijslast": [
            "UPS-systemen en testresultaten",
            "Noodstroomgenerator en periodieke testtrapport",
            "Meervoudige stroomvoeding documentatie voor kritieke systemen",
        ],
    },
    "7.12": {
        "normtekst": (
            "Bekabeling voor elektriciteit en telecommunicatie die gegevens "
            "transporteert of ondersteunende informatiediensten ondersteunt, "
            "moet worden beschermd tegen onderschepping, interferentie of schade."
        ),
        "interpretatie": (
            "Netwerkbekabeling die fysiek toegankelijk is kan worden afgeluisterd "
            "of beschadigd. Kabelgoten, afsluitbare patchkasten en scheiding "
            "van stroom- en datakabels reduceren dit risico."
        ),
        "bewijslast": [
            "Bekabelingsdocumentatie en -plattegrond",
            "Bewijs van bescherming van kritieke bekabeling (kabelgoten, afscherming)",
            "Inspectierecords van bekabelingsinfrastructuur",
        ],
    },
    "7.13": {
        "normtekst": (
            "Apparatuur moet correct worden onderhouden om de continue "
            "beschikbaarheid en integriteit te waarborgen."
        ),
        "interpretatie": (
            "Apparatuur die niet wordt onderhouden valt vaker uit en heeft "
            "een kortere levensduur. Gepland onderhoud voorkomt ongeplande "
            "uitval. Onderhoud door externe partijen moet worden beheerd "
            "vanuit beveiligingsperspectief."
        ),
        "bewijslast": [
            "Onderhoudsschema voor kritieke apparatuur",
            "Onderhoudsrecords (interne en externe onderhoud)",
            "Procedure voor beveiligingsbeheer bij extern onderhoud",
        ],
    },
    "7.14": {
        "normtekst": (
            "Onderdelen van apparatuur die opslagmedia bevatten, moeten worden "
            "geverifieerd om te waarborgen dat gevoelige gegevens en gelicentieerde "
            "software zijn gewist of veilig overschreven of vernietigd voordat "
            "de apparatuur wordt afgestoten of hergebruikt."
        ),
        "interpretatie": (
            "Laptops, servers en printers die worden afgedankt of verkocht "
            "bevatten vaak nog gevoelige data. Simpelweg formatteren is "
            "onvoldoende; gespecialiseerde wissprocedures of fysieke vernietiging "
            "zijn noodzakelijk voor kritieke data."
        ),
        "bewijslast": [
            "Procedure voor veilige dataverwijdering voor afstoting apparatuur",
            "Records van gegevenswissing (NIST 800-88 of equivalent)",
            "Certificaten van vernietiging bij fysieke vernietiging",
        ],
    },
    # ---- Technologische beheersmaatregelen (8.x) ----
    "8.1": {
        "normtekst": (
            "Informatie op gebruikerseindpuntapparaten moet worden beschermd. "
            "De organisatie moet beleid en ondersteunende technische maatregelen "
            "vaststellen voor het veilig beheren van gebruikerseindpuntapparaten."
        ),
        "interpretatie": (
            "Laptops, smartphones en tablets zijn de meest kwetsbare schakel "
            "in de beveiligingsketen. Ze gaan mee naar buiten, worden verloren "
            "en gerepareerd door derden. MDM, encryptie en remote-wipe zijn "
            "basismaatregelen."
        ),
        "bewijslast": [
            "Eindpuntbeveiligingsbeleid (BYOD, corporate devices)",
            "MDM-configuratie en compliance rapport",
            "Bewijs van encryptie op alle beheerde eindpunten",
        ],
    },
    "8.2": {
        "normtekst": (
            "Privileged access rights moeten worden beperkt en beheerd "
            "overeenkomstig het toegangsbeheersingsbeleid en de regels voor "
            "toegangsbeheersing."
        ),
        "interpretatie": (
            "Beheerdersaccounts zijn de meest waardevolle doelwitten voor "
            "aanvallers. Het principe van least privilege beperkt de schade "
            "als een account wordt gecompromitteerd. PAM-tools en aparte "
            "beheerdersaccounts zijn standaard praktijk."
        ),
        "bewijslast": [
            "Privileged Access Management (PAM) procedure",
            "Register van privileged accounts",
            "Bewijs van scheiding van beheerdersaccounts van reguliere accounts",
            "Periodieke review van privileged accounts",
        ],
    },
    "8.3": {
        "normtekst": (
            "Toegang tot informatie en andere daarmee samenhangende activa "
            "moet worden beperkt overeenkomstig het vastgestelde themaspecifieke "
            "beleid voor toegangsbeheersing."
        ),
        "interpretatie": (
            "Informatiebeperkingen worden technisch afgedwongen via bestandsrechten, "
            "databasepermissies en applicatiemachtigingen. Het beleid stelt de "
            "regels; technische implementatie zorgt voor naleving. "
            "Periodieke controle sluit de cirkel."
        ),
        "bewijslast": [
            "Toegangsrechtenconfiguratie per systeem/applicatie",
            "Resultaten van access review per systeem",
            "Bewijs van need-to-know principe in rechtenstructuur",
        ],
    },
    "8.4": {
        "normtekst": (
            "Toegang tot broncode, ontwikkelgereedschappen en software libraries "
            "moet op passende wijze worden beheerd."
        ),
        "interpretatie": (
            "Broncode bevat intellectueel eigendom en vaak hardcoded credentials "
            "of beveiligingsgevoelige logica. Ongecontroleerde toegang tot "
            "broncode vergroot het risico op sabotage, diefstal en kwetsbaarheden "
            "in productiesystemen."
        ),
        "bewijslast": [
            "Toegangsbeheersing op broncoderepositories (Git, SVN)",
            "Bewijs van code review procedure voor wijzigingen",
            "Bewijs dat productie-credentials niet in broncode worden opgeslagen",
        ],
    },
    "8.5": {
        "normtekst": (
            "Veilige authenticatieprocedures en -technologieën moeten worden "
            "geïmplementeerd op basis van beperkingen voor informatiebeheer "
            "en in overeenstemming met het themaspecifieke beleid voor "
            "toegangsbeheersing."
        ),
        "interpretatie": (
            "Wachtwoorden alleen zijn onvoldoende voor kritieke systemen. "
            "Multi-factor authenticatie, SSO en sterke authenticatieprotocollen "
            "reduceren het risico van gecompromitteerde credentials significant. "
            "De methode moet passen bij de sensitiviteit van het systeem."
        ),
        "bewijslast": [
            "MFA-implementatie op kritieke en externe toegangspunten",
            "Authenticatieconfiguratie per systeem",
            "Wachtwoordbeleid technisch afgedwongen (complexity, length, history)",
        ],
    },
    "8.6": {
        "normtekst": (
            "Het gebruik van middelen moet worden gemonitord en aangepast "
            "overeenkomstig de actuele en verwachte capaciteitseisen."
        ),
        "interpretatie": (
            "Systemen die vol raken of overbelast zijn, presteren slecht of "
            "vallen uit. Capaciteitsmonitoring voorkomt verrassingen en "
            "maakt proactieve opschaling mogelijk. Dit is ook relevant voor "
            "het voorkomen van denial-of-service effecten."
        ),
        "bewijslast": [
            "Capaciteitsmonitoringssysteem en dashboards",
            "Procedure voor capaciteitsplanning en -uitbreiding",
            "Historische capaciteitsdata en trendanalyses",
        ],
    },
    "8.7": {
        "normtekst": (
            "Bescherming tegen malware moet worden geïmplementeerd en "
            "ondersteund door passend bewustzijn van gebruikers."
        ),
        "interpretatie": (
            "Malware is een van de meest voorkomende en schadelijke dreigingen. "
            "Anti-malwareoplossingen moeten worden bijgehouden, gecombineerd "
            "met gebruikersbewustzijn over phishing en verdachte downloads. "
            "Alleen techniek of alleen bewustzijn is onvoldoende."
        ),
        "bewijslast": [
            "Anti-malware configuratie en updatebeleid",
            "Malwarescan resultaten en respons op detecties",
            "Security awareness training inclusief phishing-simulaties",
        ],
    },
    "8.8": {
        "normtekst": (
            "Informatie over technische kwetsbaarheden van gebruikte "
            "informatiesystemen moet tijdig worden verkregen, de blootstelling "
            "van de organisatie aan dergelijke kwetsbaarheden moet worden "
            "beoordeeld en passende maatregelen moeten worden genomen."
        ),
        "interpretatie": (
            "Kwetsbaarheden worden dagelijks ontdekt en gepubliceerd. Een "
            "systematisch patchproces en kwetsbaarhedenbeheer verkleint het "
            "venster van blootstelling. Niet patchen is de meest voorkomende "
            "oorzaak van succesvolle cyberaanvallen."
        ),
        "bewijslast": [
            "Kwetsbaarhedenscanresultaten (bijv. Nessus, Qualys)",
            "Patchbeheer procedure en patchstatus per systeem",
            "SLA voor patchimplementatie op basis van risiconiveau",
        ],
    },
    "8.9": {
        "normtekst": (
            "Configuraties, inclusief beveiligingsconfiguraties, van hardware, "
            "software, diensten en netwerken moeten worden vastgesteld, "
            "gedocumenteerd, geïmplementeerd, gemonitord en beoordeeld."
        ),
        "interpretatie": (
            "Standaard configuraties zijn zelden veilig. Hardening op basis "
            "van CIS benchmarks of vergelijkbare standaarden verwijdert onnodige "
            "services en sluit bekende kwetsbaarheden. Configuratiedrift is "
            "een sluipend beveiligingsrisico."
        ),
        "bewijslast": [
            "Hardening-baselines per systeem/platform (CIS benchmarks)",
            "Configuratiebeheer database (CMDB) of gelijkwaardig",
            "Bewijs van configuratiemonitoring en detectie van drift",
        ],
    },
    "8.10": {
        "normtekst": (
            "Informatie die is opgeslagen in informatiesystemen, apparaten of "
            "andere opslagmedia moet worden verwijderd wanneer deze niet langer "
            "benodigd is."
        ),
        "interpretatie": (
            "Data die je niet meer nodig hebt maar wel bewaart, is een onnodige "
            "blootstelling. Data minimalisatie (AVG-principe) en veilige "
            "verwijdering verkleinen het risico bij een datalek. "
            "Retentiebeleid bepaalt wanneer data weg mag."
        ),
        "bewijslast": [
            "Dataverwerkings- en retentiebeleid",
            "Procedure voor veilige dataverwijdering",
            "Records van uitgevoerde dataverwijdering",
        ],
    },
    "8.11": {
        "normtekst": (
            "Maatregelen voor data masking moeten worden geïmplementeerd "
            "overeenkomstig het themaspecifieke beleid voor toegangsbeheersing "
            "van de organisatie en andere gerelateerde themaspecifieke beleidslijnen "
            "en bedrijfseisen, rekening houdend met toepasselijke wetgeving."
        ),
        "interpretatie": (
            "Test- en ontwikkelomgevingen mogen geen echte persoonsgegevens "
            "bevatten. Data masking, anonimisering en pseudonimisering "
            "beschermen privacy in niet-productieomgevingen. Dit is ook een "
            "AVG-verplichting."
        ),
        "bewijslast": [
            "Beleid voor gebruik van testdata",
            "Bewijs van data masking in test-/ontwikkelomgevingen",
            "Procedure voor pseudonimisering of anonimisering",
        ],
    },
    "8.12": {
        "normtekst": (
            "Maatregelen voor preventie van datalekken moeten worden toegepast "
            "op systemen, netwerken en andere apparaten die gevoelige informatie "
            "verwerken, opslaan of transporteren."
        ),
        "interpretatie": (
            "DLP-technologie detecteert en blokkeert ongeautoriseerde "
            "informatieoverdracht (e-mail, USB, cloud upload). Het is een "
            "technische vangnet voor gevallen waar beleid en training "
            "onvoldoende zijn gebleken."
        ),
        "bewijslast": [
            "DLP-beleid en technische implementatie",
            "DLP-incidentenrapportage en opvolging",
            "Bewijs van monitoring op uitvoer van gevoelige data",
        ],
    },
    "8.13": {
        "normtekst": (
            "Back-upkopieën van informatie, software en systemen moeten worden "
            "gemaakt en regelmatig worden getest overeenkomstig het overeengekomen "
            "themaspecifieke beleid voor back-up."
        ),
        "interpretatie": (
            "Back-ups zijn de laatste verdedigingslinie tegen ransomware, "
            "datastoringen en menselijke fouten. Ongeteste back-ups zijn "
            "geen garantie. 3-2-1 regel (3 kopieën, 2 media, 1 offsite) "
            "is de basisnorm."
        ),
        "bewijslast": [
            "Back-upbeleid met RPO/RTO per systeem",
            "Back-uptestresultaten (restore tests)",
            "Bewijs van offsite of offline back-upopslag",
        ],
    },
    "8.14": {
        "normtekst": (
            "Informatiefaciliteiten moeten met voldoende redundantie worden "
            "geïmplementeerd om te voldoen aan beschikbaarheidseisen."
        ),
        "interpretatie": (
            "Kritieke systemen mogen geen single point of failure hebben. "
            "Redundantie (dubbele stroomtoevoer, failover-servers, "
            "load balancing) waarborgt beschikbaarheid ook bij storingen. "
            "De mate van redundantie moet aansluiten bij de bedrijfsbehoefte."
        ),
        "bewijslast": [
            "Architectuurdocumentatie met redundantiemaatregelen",
            "SLA's met beschikbaarheidsgaranties",
            "Failover-testresultaten",
        ],
    },
    "8.15": {
        "normtekst": (
            "Logboeken die activiteiten, uitzonderingen, fouten en andere "
            "relevante gebeurtenissen vastleggen, moeten worden geproduceerd, "
            "opgeslagen, beschermd en geanalyseerd."
        ),
        "interpretatie": (
            "Logging is de basis voor detectie, forensisch onderzoek en "
            "compliance. Logs moeten volledig, integer en voldoende lang "
            "bewaard zijn. Logs die alleen worden aangemaakt maar nooit "
            "worden geanalyseerd, hebben beperkte waarde."
        ),
        "bewijslast": [
            "Logbeleid (welke systemen loggen wat, retentietermijn)",
            "Bewijs van gecentraliseerde logopslag (SIEM)",
            "Bewijs van log-integriteitsbeveiliging (tamper protection)",
            "Bewijs van periodieke loganalyse of alerting",
        ],
    },
    "8.16": {
        "normtekst": (
            "Netwerken en systemen moeten worden gemonitord op afwijkend "
            "gedrag en passende maatregelen moeten worden genomen om potentiële "
            "informatiebeveiligingsincidenten te evalueren."
        ),
        "interpretatie": (
            "Monitoring detecteert aanvallen die preventieve maatregelen hebben "
            "omzeild. SIEM, IDS/IPS en anomaliedetectie zijn standaard tools. "
            "Monitoring heeft alleen waarde als er ook wordt gereageerd op "
            "alerts: een SOC of on-call procedure is noodzakelijk."
        ),
        "bewijslast": [
            "Monitoring- en alertingsysteem (SIEM, IDS)",
            "Alert response procedure",
            "Bewijs van opvolging van monitoringwaarschuwingen",
        ],
    },
    "8.17": {
        "normtekst": (
            "Klokken van informatieverwerkingssystemen die door de organisatie "
            "worden gebruikt, moeten worden gesynchroniseerd met goedgekeurde "
            "tijdbronnen."
        ),
        "interpretatie": (
            "Tijdsynchronisatie (NTP) is essentieel voor log-correlatie bij "
            "incidentonderzoek. Als systemen verschillende tijden hebben, "
            "is het reconstrueren van een aanval veel moeilijker. "
            "Dit is een eenvoudige maar kritieke maatregel."
        ),
        "bewijslast": [
            "NTP-configuratie op alle systemen",
            "Bewijs van gecentraliseerde tijdbron",
            "Monitoring op tijdafwijkingen",
        ],
    },
    "8.18": {
        "normtekst": (
            "Het gebruik van programma's met speciale beheerdersrechten "
            "die systeembeheersing kunnen omzeilen, moet worden beperkt "
            "en nauwkeurig worden bewaakt."
        ),
        "interpretatie": (
            "Utilities als netwerk-scanners, password crackers en directe "
            "databasetoegang zijn krachtige tools die ook door kwaadwillenden "
            "worden gebruikt. Gebruik moet geautoriseerd, beperkt en gelogd "
            "zijn."
        ),
        "bewijslast": [
            "Register van geautoriseerde beheerhulpprogramma's",
            "Procedure voor gebruik en logging van privileged utilities",
            "Bewijs van beperkte toegang tot systeembeheerhulpmiddelen",
        ],
    },
    "8.19": {
        "normtekst": (
            "Procedures en maatregelen voor de installatie van software op "
            "operationele systemen moeten worden geïmplementeerd."
        ),
        "interpretatie": (
            "Ongecontroleerde software-installatie is een veelvoorkomende "
            "bron van kwetsbaarheden en malware-infecties. Whitelisting, "
            "applicatiecatalogi en goedkeuringsprocessen beperken dit risico. "
            "Eindgebruikers mogen geen software installeren zonder toestemming."
        ),
        "bewijslast": [
            "Software installatie- en goedkeuringsbeleid",
            "Technische afdwinging (applicatie whitelisting of AppLocker)",
            "Bewijs van softwareinventarisatie en compliance",
        ],
    },
    "8.20": {
        "normtekst": (
            "Netwerken en netwerkapparaten moeten worden beveiligd, beheerd "
            "en bewaakt om informatie en informatiefaciliteiten te beschermen."
        ),
        "interpretatie": (
            "Het netwerk is de ruggengraat van informatieverwerking. "
            "Firewalls, netwerksegmentatie, veilige protocollen en "
            "netwerkmapping zijn basisvereisten. Een slecht beveiligd netwerk "
            "maakt andere maatregelen minder effectief."
        ),
        "bewijslast": [
            "Netwerkarchitectuurdocumentatie",
            "Firewallregels en change management procedure",
            "Bewijs van netwerksegmentatie (VLAN, DMZ)",
            "Netwerkmonitoringrapportages",
        ],
    },
    "8.21": {
        "normtekst": (
            "Beveiligingsmechanismen, service niveaus en beheersvereisten voor "
            "alle netwerkdiensten moeten worden geïdentificeerd, geïmplementeerd "
            "en gemonitord, of deze diensten nu intern worden geleverd of "
            "uitbesteed zijn."
        ),
        "interpretatie": (
            "Netwerkdiensten (DNS, DHCP, e-mail, VPN) moeten elk hun eigen "
            "beveiligingsconfiguratie hebben. Uitbestede netwerkdiensten "
            "vereisen contractuele beveiligingsgaranties en monitoring op "
            "naleving."
        ),
        "bewijslast": [
            "Inventaris van netwerkdiensten met beveiligingsconfiguratie",
            "SLA's voor externe netwerkdiensten met beveiligingseisen",
            "Bewijs van monitoring op netwerkdienstenprestaties en beveiliging",
        ],
    },
    "8.22": {
        "normtekst": (
            "Groepen van informatiediensten, gebruikers en informatiesystemen "
            "moeten in netwerken worden gesegmenteerd."
        ),
        "interpretatie": (
            "Netwerksegmentatie beperkt de schade als een aanvaller toegang "
            "krijgt tot één segment: laterale beweging wordt bemoeilijkt. "
            "Kritieke systemen (OT, financieel, HR) moeten in aparte segmenten "
            "met strikte toegangsregels."
        ),
        "bewijslast": [
            "Netwerksegmentatiearchitectuur (VLAN, firewall zones)",
            "Bewijs van scheiding productie-, test- en beheersegmenten",
            "Firewallregels tussen segmenten en audit van regelsets",
        ],
    },
    "8.23": {
        "normtekst": (
            "Toegang tot externe websites moet worden beheerd om blootstelling "
            "aan kwaadaardige content te verminderen."
        ),
        "interpretatie": (
            "Webfiltering blokkeert toegang tot kwaadaardige, ongepaste of "
            "niet-zakelijke websites. Dit verkleint het risico van drive-by "
            "downloads, phishing en datalekkage. De filterregels moeten "
            "worden bijgehouden en afgestemd op bedrijfsbehoeften."
        ),
        "bewijslast": [
            "Webfilterbeleid en categorie-instellingen",
            "Webfilter configuratie en rapportages",
            "Procedure voor whitelist/blacklist uitzonderingen",
        ],
    },
    "8.24": {
        "normtekst": (
            "Regels voor het gebruik van cryptografie, inclusief beheer van "
            "cryptografische sleutels, moeten worden vastgesteld en geïmplementeerd."
        ),
        "interpretatie": (
            "Cryptografie beschermt data in rust en in transit. Maar slecht "
            "sleutelbeheer ondermijnt de sterkste encryptie. Je moet expliciet "
            "bepalen welke algoritmen worden gebruikt, hoe sleutels worden "
            "opgeslagen en wanneer ze worden vervangen."
        ),
        "bewijslast": [
            "Cryptografiebeleid (algoritmen, sleutellengtes, protocollen)",
            "Sleutelbeheer procedure (generatie, opslag, rotatie, intrekking)",
            "Bewijs van encryptie in transit (TLS-configuratie) en in rust",
        ],
    },
    "8.25": {
        "normtekst": (
            "Regels voor de veilige ontwikkeling van software en systemen moeten "
            "worden vastgesteld en toegepast op ontwikkelingen binnen de organisatie."
        ),
        "interpretatie": (
            "Security moet worden ingebakken in het ontwikkelproces, niet er "
            "achteraf in worden gestopt. Secure coding standards, security "
            "reviews en SAST-tools zijn onderdeel van een volwassen "
            "ontwikkelproces."
        ),
        "bewijslast": [
            "Secure development lifecycle (SDLC) procedure",
            "Secure coding guidelines",
            "Bewijs van security reviews in het ontwikkelproces",
        ],
    },
    "8.26": {
        "normtekst": (
            "Informatiebeveiligingseisen moeten worden geïdentificeerd, "
            "gespecificeerd en goedgekeurd bij het ontwikkelen of verwerven "
            "van applicaties."
        ),
        "interpretatie": (
            "Applicatiebeveiligingseisen moeten worden bepaald voordat "
            "ontwikkeling of inkoop begint. Achteraf toevoegen van beveiliging "
            "is duurder en levert minder robuuste resultaten. Dit geldt ook "
            "voor SaaS en commerciële pakketten."
        ),
        "bewijslast": [
            "Beveiligingseisen in systeemspecificaties of RFP's",
            "Security requirements per applicatieclassificatie",
            "Bewijs van beveiligingsbeoordeling bij aanschaf of oplevering",
        ],
    },
    "8.27": {
        "normtekst": (
            "Principes voor het ontwerpen van veilige systemen moeten worden "
            "vastgesteld, gedocumenteerd, onderhouden en toegepast op "
            "informatiесysteem-implementatiewerkzaamheden."
        ),
        "interpretatie": (
            "Principes als least privilege, defense in depth, fail secure "
            "en zero trust moeten worden verankerd in het ontwerpproces. "
            "Door deze principes expliciet te maken, worden ze reproduceerbaar "
            "toegepast in nieuwe systemen."
        ),
        "bewijslast": [
            "Security by design principes document",
            "Bewijs van toepassing in architectuurreviews",
            "Security architecture review records voor nieuwe systemen",
        ],
    },
    "8.28": {
        "normtekst": (
            "Veilige codeerpraktijken moeten worden toegepast op "
            "softwareontwikkeling."
        ),
        "interpretatie": (
            "OWASP Top 10 kwetsbaarheden (SQL-injectie, XSS, etc.) zijn "
            "al decennia bekend en toch komen ze nog steeds voor. Secure "
            "coding training, peer reviews en SAST-tools reduceren deze "
            "kwetsbaarheden systematisch."
        ),
        "bewijslast": [
            "Secure coding standaard (OWASP of equivalent)",
            "SAST/DAST-toolresultaten in CI/CD pipeline",
            "Bewijs van code review voor beveiligingsgerelateerde wijzigingen",
        ],
    },
    "8.29": {
        "normtekst": (
            "Beveiligingstestprocessen moeten worden gedefinieerd en "
            "geïmplementeerd in de ontwikkellevenscyclus."
        ),
        "interpretatie": (
            "Testen voor ingebruikname detecteert beveiligingsfouten voordat "
            "ze in productie komen. Penetratietests, vulnerability scans en "
            "security acceptance tests zijn onderdeel van een volwassen "
            "testproces."
        ),
        "bewijslast": [
            "Beveiligingstestprocedure in SDLC",
            "Penetratietestrapportages en opvolging bevindingen",
            "Security acceptance test criteria en resultaten",
        ],
    },
    "8.30": {
        "normtekst": (
            "Uitbestede ontwikkeling moet worden gesuperviseerd en gemonitord "
            "door de organisatie."
        ),
        "interpretatie": (
            "Als ontwikkeling wordt uitbesteed, behoud je als organisatie "
            "de verantwoordelijkheid voor de beveiliging van het eindproduct. "
            "Contractuele eisen, code reviews en beveiligingstests moeten "
            "ook bij uitbesteding worden gewaarborgd."
        ),
        "bewijslast": [
            "Contractuele beveiligingseisen voor uitbestede ontwikkeling",
            "Bewijs van beveiligingsbeoordeling opgeleverde code",
            "Procedure voor acceptatietests bij uitbestede ontwikkeling",
        ],
    },
    "8.31": {
        "normtekst": (
            "Ontwikkel-, test- en productieomgevingen moeten van elkaar worden "
            "gescheiden en beveiligd."
        ),
        "interpretatie": (
            "Ontwikkelaars die directe toegang hebben tot productiesystemen "
            "zijn een significant risico. Omgevingsscheiding voorkomt dat "
            "testactiviteiten productie verstoren en dat productiedata in "
            "ontwikkelomgevingen terechtkomen."
        ),
        "bewijslast": [
            "Documentatie van omgevingsscheiding (DTAP)",
            "Toegangsbeheersing per omgeving",
            "Procedure voor promotie van code tussen omgevingen",
        ],
    },
    "8.32": {
        "normtekst": (
            "Wijzigingen in informatiefaciliteiten en informatiesystemen moeten "
            "worden beheerst door middel van wijzigingsbeheer procedures."
        ),
        "interpretatie": (
            "Ongecontroleerde wijzigingen zijn een van de grootste oorzaken "
            "van storingen en beveiligingsincidenten. Change management "
            "zorgt voor beoordeling, goedkeuring, testen en documentatie "
            "van elke wijziging in productieomgevingen."
        ),
        "bewijslast": [
            "Change management procedure (CAB of equivalent)",
            "Change log met alle wijzigingen en goedkeuringsrecords",
            "Bewijs van impact- en risicoanalyse per change",
            "Rollback procedure per change",
        ],
    },
    "8.33": {
        "normtekst": (
            "Testinformatie moet worden geselecteerd, beschermd en beheerd."
        ),
        "interpretatie": (
            "Testomgevingen bevatten vaak kopieën van productiedata. Als "
            "testdata niet wordt beschermd, kan gevoelige informatie lekken "
            "via ontwikkelaars of leveranciers. Data masking of synthetische "
            "testdata zijn de oplossing."
        ),
        "bewijslast": [
            "Beleid voor gebruik en bescherming van testdata",
            "Bewijs van data masking of anonimisering in testomgevingen",
            "Toegangsbeheersing op testomgevingen met gevoelige data",
        ],
    },
    "8.34": {
        "normtekst": (
            "Informatiesystemen moeten worden beschermd tijdens audittests om "
            "verstoring van bedrijfsprocessen en gebruikte auditgereedschappen "
            "te minimaliseren."
        ),
        "interpretatie": (
            "Audittests (penetratietests, vulnerability scans) kunnen systemen "
            "belasten of tijdelijk verstoren. Door goede afspraken te maken "
            "over scope, timing en autorisatie voorkom je onnodige verstoring "
            "en juridische problemen."
        ),
        "bewijslast": [
            "Geautoriseerde scope en planning voor audittests",
            "Schriftelijke toestemming voor penetratietests",
            "Procedure voor beheer van audittools en -toegang",
        ],
    },
}
