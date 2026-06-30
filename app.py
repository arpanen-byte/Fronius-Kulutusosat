import streamlit as st
import pandas as pd
import os

# Sivun asetukset ja leveä asettelu koontitaulukoille
st.set_page_config(page_title="Fronius-varaosahaku Pro", page_icon="🔥", layout="wide")

st.title("Fronius Kulutusosat (Nimi- tai koodihaku)")
st.write("Voit hakea osia lennosta joko kirjoittamalla tuotenumeron, osan nimen, laitteen mallin, kuvasto päivittyy ajoittain.")

# Varmistetaan, että Excel-tiedosto löytyy
excel_tiedosto = "varaosat.xlsx"

if not os.path.exists(excel_tiedosto):
    st.error(f"❌ Tiedostoa '{excel_tiedosto}' ei löytynyt samasta kansiosta koodin kanssa!")
    st.info("Varmista, että olet tallentanut Excel-taulukon koodin viereen nimellä **varaosat.xlsx**.")
else:
    # Älykäs lataus muokkausajan mukaan
    @st.cache_data
    def lataa_data(tiedostopolku, muokkausaika):
        return pd.read_excel(tiedostopolku)
    
    tiedoston_muokkausaika = os.path.getmtime(excel_tiedosto)
    df = lataa_data(excel_tiedosto, tiedoston_muokkausaika)

    # ==============================================================================
    # LAAJENNETTU: NIMI- JA KOODI-PÍKAHAKU (YHDISTETTY HAKUKENTTÄ)
    # ==============================================================================
    st.subheader("🔍 Pikahaku nimellä tai tuotenumerolla")
    hakusana = st.text_input(
        "Kirjoita tähän hakusana (esim. eriste, kaasusuutin, MTW, AW4000 tai Fronius-koodi):", 
        placeholder="Mitä osaa, mallia tai numeroa etsit?..."
    ).strip()

    # Jos hakukentässä on tekstiä, tutkitaan kaikki olennaiset sarakkeet
    if hakusana:
        ehdot = (
            df['Tuotenumero'].astype(str).str.contains(hakusana, case=False, na=False) |
            df['Komponentti / Osa'].astype(str).str.contains(hakusana, case=False, na=False) |
            df['Tuoteperhe / Malli'].astype(str).str.contains(hakusana, case=False, na=False) |
            df['Varustelu / Tyyppi / Koko'].astype(str).str.contains(hakusana, case=False, na=False)
        )
        
        tulokset = df[ehdot]
        
        st.divider()
        if not tulokset.empty:
            st.success(f"🎯 **Löytyi {len(tulokset)} osumaa hakusanalle: '{hakusana}'**")
            # Näytetään tulokset selkeänä taulukkona
            st.table(tulokset.reset_index(drop=True))
        else:
            st.error(f"😞 Hakusanalla '{hakusana}' ei löytynyt yhtään osaa. Tarkista kirjoitusasu.")
            
    # Jos hakukenttä on tyhjä, näytetään perinteinen kategoriaselaus
    else:
        st.divider()
        st.subheader("📁 Selaa varaosaluetteloa kriteereillä")

        # 1. Pääkategorian valinta
        paakategoriat = df['Pääkategoria'].dropna().unique()
        valittu_paakategoria = st.selectbox("Valitse haettava tuotetyyppi:", paakategoriat)
        df_suodatettu = df[df['Pääkategoria'] == valittu_paakategoria]

        # 2. Mallin / Tuoteperheen valinta
        mallit = df_suodatettu['Tuoteperhe / Malli'].dropna().unique()
        valittu_malli = st.selectbox("Valitse mallisarja / teholuokka:", mallit)
        df_lopullinen = df_suodatettu[df_suodatettu['Tuoteperhe / Malli'] == valittu_malli]

        st.divider()

        # 3. Tulostus taulukkona
        st.info(f"📊 **Näytetään tiedot kohteelle:** {valittu_malli}")
        
        naytettavat_sarakkeet = []
        for col in ['Varustelu / Tyyppi / Koko', 'Komponentti / Osa', 'Tuotenumero', 'Lisätiedot / Säännöt']:
            if col in df_lopullinen.columns:
                naytettavat_sarakkeet.append(col)
                
        if naytettavat_sarakkeet:
            st.table(df_lopullinen[naytettavat_sarakkeet].reset_index(drop=True))
        else:
            st.table(df_lopullinen)