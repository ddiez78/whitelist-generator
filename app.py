from flask import Flask, render_template_string, request, send_file, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import urljoin, urlparse
import io
import os

app = Flask(__name__)

class WhitelistGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # URLs pre-seleccionadas de medios confiables por país, ordenadas aproximadamente por volumen de tráfico
        self.medios_confiables = {
            'Brasil': [
                'https://www.globo.com/', 'https://www.uol.com.br/', 'https://www.r7.com/',
                'https://www.folha.uol.com.br/', 'https://oglobo.globo.com/', 'https://www.estadao.com.br/',
                'https://www.band.uol.com.br/', 'https://www.terra.com.br/', 'https://www.em.com.br/',
                'https://www.correiobraziliense.com.br/', 'https://www.abc.com.br/', 'https://www.jovempan.com.br/',
                'https://www.cnnbrasil.com.br/', 'https://www.abril.com.br/', 'https://veja.abril.com.br/',
                'https://exame.com/', 'https://www.valorinveste.globo.com/', 'https://www.economist.com/brazil',
                'https://www.mediainfo.com.br/', 'https://www.iberonews.com.br/', 'https://gauchazh.clicrbs.com.br/',
                'https://www1.folha.uol.com.br/', 'https://www.diariodaregiao.com.br/', 'https://www.otvfoco.com.br/',
                'https://www.panrotas.com.br/', 'https://www.ecycle.com.br/', 'https://www.tecmundo.com.br/',
                'https://www.canaltech.com.br/', 'https://www.megacurioso.com.br/', 'https://www.guiadavida.com.br/',
                'https://www.infomoney.com.br/', 'https://www.istoedinheiro.com.br/', 'https://www.cartacapital.com.br/',
                'https://www.revistaoeste.com/', 'https://www.jota.info/', 'https://www.congressonacional.com.br/',
                'https://www.camara.leg.br/', 'https://www.senado.leg.br/', 'https://www.planalto.gov.br/',
                'https://www.gov.br/', 'https://www.bcb.gov.br/', 'https://www.anvisa.gov.br/',
                'https://www.ibge.gov.br/', 'https://www.ans.gov.br/', 'https://www.previdencia.gov.br/',
                'https://www.receita.fazenda.gov.br/', 'https://www.trabalho.gov.br/', 'https://www.justica.gov.br/'
            ],
            'Perú': [
                'https://www.larepublica.pe/', 'https://elcomercio.pe/', 'https://rpp.pe/',
                'https://gestion.pe/', 'https://www.peru21.pe/', 'https://www.trome.pe/',
                'https://andina.pe/', 'https://www.ojo-publico.com/', 'https://www.laprensa.com.pe/',
                'https://www.peru.com/', 'https://www.mundoperu.com/', 'https://www.noticiasperu.com/',
                'https://gestion.pe/economia/', 'https://elcomercio.pe/economia/', 'https://www.expreso.com.pe/',
                'https://www.elperuano.pe/', 'https://www.andina.pe/agencia/', 'https://www.panorama.com.uy/peru/',
                'https://www.iberonews.com.pe/', 'https://www.gestion.pe/politica/', 'https://www.peru21.pe/opinion/',
                'https://trome.pe/', 'https://diariolaregion.com.pe/', 'https://www.ultimahora.pe/',
                'https://www.liderendeportes.com/', 'https://www.ecured.cu/', 'https://www.elperuano.com.pe/',
                'https://www.larepublica.net/', 'https://www.elcomercio.com/', 'https://www.rppnoticias.pe/',
                'https://www.noticiasperu.com/', 'https://www.peru.info/', 'https://www.peru.travel/',
                'https://www.promperu.gob.pe/', 'https://www.mininter.gob.pe/', 'https://www.minagri.gob.pe/',
                'https://www.minsa.gob.pe/', 'https://www.minedu.gob.pe/', 'https://www.sunat.gob.pe/',
                'https://www.bcrp.gob.pe/', 'https://www.trabajo.gob.pe/', 'https://www.minem.gob.pe/',
                'https://www.mininterior.gob.pe/', 'https://www.munimelgar.gob.pe/'
            ],
            'Argentina': [
                'https://www.clarin.com/', 'https://www.lanacion.com.ar/', 'https://www.infobae.com/',
                'https://www.telam.com.ar/', 'https://www.pagina12.com.ar/', 'https://www.ambito.com/',
                'https://www.perfil.com/', 'https://www.ole.com.ar/', 'https://www.lavoz.com.ar/',
                'https://www.rosario3.com/', 'https://www.cronista.com/', 'https://www.tycsports.com/',
                'https://www.abc.com.py/', 'https://www.misionesonline.net/', 'https://www.diariopanorama.com/',
                'https://www.diariodecuyo.com.ar/', 'https://www.eldiarioexterior.com/', 'https://www.ellitoral.com/',
                'https://www.lacapital.com.ar/', 'https://www.diarioregistrado.com/', 'https://www.losandes.com.ar/',
                'https://www.diario26.com/', 'https://www.elpopular.com.ar/', 'https://www.laprensa.com.ar/',
                'https://www.diariouno.com.ar/', 'https://www.lacapital.com.ar/', 'https://www.lavanguardia.com.ar/',
                'https://www.diariodemocracia.com/', 'https://www.elliberal.com.ar/', 'https://www.diariocronica.com.ar/',
                'https://www.diariocriticoweb.com.ar/', 'https://www.diarioregional.com.ar/', 'https://www.diariopartidario.com.ar/',
                'https://www.diariodeculturayturismo.com.ar/', 'https://www.diariodelviajero.com.ar/', 'https://www.diariodelnorte.com.ar/',
                'https://www.diariodelsur.com.ar/'
            ],
            'Uruguay': [
                'https://www.elpais.com.uy/', 'https://www.larepublica.com.uy/', 'https://www.observatoriomultimedia.org.uy/',
                'https://www.subrayado.com.uy/', 'https://www.180.com.uy/', 'https://www.carasycaretas.com.uy/',
                'https://www.21mujeres.com.uy/', 'https://www.veinteminutos.com.uy/', 'https://www.elperiodicouruguay.com/',
                'https://www.elpueblo.com.uy/', 'https://www.diariolaregional.com.uy/', 'https://www.diariolibre.com.uy/',
                'https://www.diariopuntadeleste.com.uy/', 'https://www.diariodecanelones.com.uy/', 'https://www.diariodecolon.com.uy/',
                'https://www.diariodelsur.com.uy/', 'https://www.diariomontevideo.com.uy/', 'https://www.diariopelotas.com.br/',
                'https://www.iberonews.com.uy/', 'https://www.montevideo.com.uy/', 'https://www.montevideo.gub.uy/',
                'https://www.gub.uy/', 'https://www.presidencia.gub.uy/', 'https://www.ministeriodeeducacion.gub.uy/',
                'https://www.mides.gub.uy/', 'https://www.msp.gub.uy/', 'https://www.uruguay.gub.uy/',
                'https://www.anticorrupcion.gub.uy/', 'https://www.uruguayxxi.gub.uy/', 'https://www.export.gov.uy/',
                'https://www.institucional.gub.uy/', 'https://www.parlamento.gub.uy/', 'https://www.cndh.gub.uy/',
                'https://www.impo.gub.uy/', 'https://www.bcu.gub.uy/', 'https://www.bps.gub.uy/',
                'https://www.brou.com.uy/', 'https://www.antel.com.uy/', 'https://www.ose.com.uy/',
                'https://www.ute.com.uy/', 'https://www.ancap.com.uy/', 'https://www.umc.edu.uy/',
                'https://www.udelar.edu.uy/', 'https://www.ort.edu.uy/', 'https://www.cat.edu.uy/'
            ],
            'Suiza': [
                'https://www.blick.ch/', 'https://www.nzz.ch/', 'https://www.tagesanzeiger.ch/',
                'https://www.20min.ch/', 'https://www.srf.ch/', 'https://www.rts.ch/',
                'https://www.rsi.ch/', 'https://www.rtr.ch/', 'https://www.swissinfo.ch/',
                'https://www.letemps.ch/', 'https://www.lematin.ch/', 'https://www.lenouvelliste.ch/',
                'https://www.tio.ch/', 'https://www.quotidiano.ch/', 'https://www.baselinerzeitung.ch/',
                'https://www.bernerzeitung.ch/', 'https://www.stettlerzeitung.ch/', 'https://www.zsz.ch/',
                'https://www.zuercherunterland.ch/', 'https://www.zuonline.ch/', 'https://www.nau.ch/',
                'https://www.derbund.ch/', 'https://www.sonntagsblick.ch/', 'https://www.woz.ch/',
                'https://www.admin.ch/', 'https://www.parlament.ch/', 'https://www.eda.admin.ch/',
                'https://www.efd.admin.ch/', 'https://www.arem.admin.ch/', 'https://www.bfs.admin.ch/',
                'https://www.foen.admin.ch/', 'https://www.swisscovery.slsp.ch/', 'https://www.ethz.ch/',
                'https://www.unige.ch/', 'https://www.unil.ch/', 'https://www.unibe.ch/',
                'https://www.epfl.ch/', 'https://www.unisg.ch/', 'https://www.unilu.ch/',
                'https://www.hsr.ch/', 'https://www.fhnw.ch/', 'https://www.zhaw.ch/',
                'https://www.hes-so.ch/', 'https://www.swissgrid.ch/', 'https://www.sbb.ch/',
                'https://www.swiss.com/', 'https://www.swissmedicalnetwork.com/', 'https://www.helsana.ch/',
                'https://www.visana.ch/', 'https://www.asso-sante.ch/', 'https://www.kss.ma/',
                'https://www.hug.ch/', 'https://www.insel.ch/', 'https://www.usz.ch/',
                'https://www.luks.ch/', 'https://www.hirslanden.ch/'
            ],
            'Bélgica': [
                'https://www.rtbf.be/', 'https://www.sudinfo.be/', 'https://www.lalibre.be/',
                'https://www.levif.be/', 'https://www.trends.be/', 'https://www.dhnet.be/',
                'https://www.lavenir.net/', 'https://www.nieuwsblad.be/', 'https://www.standaard.be/',
                'https://www.hln.be/', 'https://www.vrt.be/', 'https://www.knack.be/',
                'https://www.bedetheque.com/', 'https://www.lesoir.be/', 'https://www.cqfd.be/',
                'https://www.mediapart.be/', 'https://www.francetvsport.fr/', 'https://www.eurogamer.be/',
                'https://www.technologie.be/', 'https://www.futura-sciences.be/', 'https://www.sciences.be/',
                'https://www.irisnet.be/', 'https://www.skynet.be/', 'https://www.voo.be/',
                'https://www.proximus.be/', 'https://www.orange.be/', 'https://www.base.be/',
                'https://www.mobistar.be/', 'https://www.telenet.be/', 'https://www.visionplurielle.be/',
                'https://www.radiofrance.be/', 'https://www.brusselslife.be/', 'https://www.igen.fr/',
                'https://www.igen.be/', 'https://www.igen.lu/', 'https://www.igen.mc/',
                'https://www.igen.sn/', 'https://www.igen.ci/', 'https://www.igen.cm/',
                'https://www.igen.tg/', 'https://www.igen.ga/', 'https://www.igen.cg/',
                'https://www.igen.cd/', 'https://www.igen.bi/', 'https://www.igen.rw/',
                'https://www.igen.mg/', 'https://www.igen.ke/', 'https://www.igen.ug/',
                'https://www.igen.tz/', 'https://www.igen.mw/', 'https://www.igen.zm/',
                'https://www.igen.mz/', 'https://www.igen.zw/', 'https://www.igen.na/',
                'https://www.igen.bw/', 'https://www.igen.ls/', 'https://www.igen.sz/',
                'https://www.igen.za/'
            ],
            'Portugal': [
                'https://www.publico.pt/', 'https://www.dn.pt/', 'https://www.jn.pt/',
                'https://www.cmjornal.pt/', 'https://www.rtp.pt/', 'https://www.sapo.pt/',
                'https://www.iol.pt/', 'https://www.expresso.pt/', 'https://www.record.pt/',
                'https://www.abola.pt/', 'https://www.futebol365.pt/', 'https://www.jornaldenegocios.pt/',
                'https://www.dinheirovivo.pt/', 'https://www.economico.sapo.pt/', 'https://www.jornalcontabilistico.pt/',
                'https://www.mercurynews.com.pt/', 'https://www.noticiaslusofonas.com/', 'https://www.lusiadas.pt/',
                'https://www.portugalglobal.pt/', 'https://www.portugal.gov.pt/', 'https://www.presidencia.pt/',
                'https://www.parlamento.pt/', 'https://www.assembleiamunicipal.cm-lisboa.pt/', 'https://www.cm-lisboa.pt/',
                'https://www.cm-porto.pt/', 'https://www.cm-braga.pt/', 'https://www.cm-guimaraes.pt/',
                'https://www.cm-benfica.pt/', 'https://www.cm-albufeira.pt/', 'https://www.cm-faro.pt/',
                'https://www.cm-sines.pt/', 'https://www.cm-setubal.pt/', 'https://www.cm-loulé.pt/',
                'https://www.cm-silves.pt/', 'https://www.cm-portimão.pt/', 'https://www.cm-tavira.pt/',
                'https://www.cm-olhão.pt/', 'https://www.cm-vilamoura.pt/', 'https://www.cm-cascais.pt/',
                'https://www.cm-estoril.pt/', 'https://www.cm-sintra.pt/', 'https://www.cm-mafra.pt/',
                'https://www.cm-oeiras.pt/', 'https://www.cm-amadora.pt/', 'https://www.cm-odivelas.pt/',
                'https://www.cm-loures.pt/', 'https://www.cm-vfx.pt/', 'https://www.cm-maia.pt/',
                'https://www.cm-matosinhos.pt/', 'https://www.cm-vncamp.pt/', 'https://www.cm-valongo.pt/',
                'https://www.cm-paredes.pt/', 'https://www.cm-penafiel.pt/', 'https://www.cm-lousada.pt/',
                'https://www.cm-trofa.pt/'
            ],
            'Holanda': [
                'https://www.nu.nl/', 'https://www.telegraaf.nl/', 'https://www.ad.nl/',
                'https://www.volkskrant.nl/', 'https://www.trouw.nl/', 'https://www.parool.nl/',
                'https://www.nrc.nl/', 'https://www.fd.nl/', 'https://www.metronieuws.nl/',
                'https://www.rtlnieuws.nl/', 'https://www.nos.nl/', 'https://www.omroep.nl/',
                'https://www.kijk.nl/', 'https://www.sanomagames.nl/', 'https://www.destentor.nl/',
                'https://www.gelderlander.nl/', 'https://www.algemeendagblad.nl/', 'https://www.bd.nl/',
                'https://www.bndestem.nl/', 'https://www.destentor.nl/', 'https://www.ed.nl/',
                'https://www.hln.be/', 'https://www.pzc.nl/', 'https://www.tctubantia.nl/',
                'https://www.valedenhavalk.nl/', 'https://www.haarenuvalk.nl/', 'https://www.mijnparool.nl/',
                'https://www.gld.nl/', 'https://www.mijnpcloud.nl/', 'https://www.knmi.nl/',
                'https://www.rijkswaterstaat.nl/', 'https://www.defensie.nl/', 'https://www.politie.nl/',
                'https://www.belastingdienst.nl/', 'https://www.douane.nl/', 'https://www.iamsterdam.com/',
                'https://www.holland.com/', 'https://www.netherlandsworldwide.nl/', 'https://www.government.nl/',
                'https://www.parlement.com/', 'https://www.tweedekamer.nl/', 'https://www.eerstekamer.nl/',
                'https://www.rijksoverheid.nl/', 'https://www.minbzk.nl/', 'https://www.minfin.nl/',
                'https://www.minvenj.nl/', 'https://www.minasw.nl/', 'https://www.minlnv.nl/',
                'https://www.minbuza.nl/', 'https://www.minvw.nl/', 'https://www.minjenvw.nl/',
                'https://www.minocw.nl/', 'https://www.minazc.nl/', 'https://www.rijkshuisvesting.nl/'
            ],
            'Reino Unido': [
                'https://www.bbc.co.uk/', 'https://www.theguardian.com/', 'https://www.telegraph.co.uk/',
                'https://www.independent.co.uk/', 'https://www.ft.com/', 'https://www.skysports.com/',
                'https://www.metro.co.uk/', 'https://www.dailymail.co.uk/', 'https://www.thesun.co.uk/',
                'https://www.express.co.uk/', 'https://www.newscientist.com/', 'https://www.economist.com/',
                'https://www.timeshighereducation.com/', 'https://www.autocar.co.uk/', 'https://www.cyclingweekly.com/',
                'https://www.bbcgoodfood.com/', 'https://www.which.co.uk/', 'https://www.money.co.uk/',
                'https://www.rightmove.co.uk/', 'https://www.telegraph.co.uk/travel/', 'https://www.independent.co.uk/travel/',
                'https://www.thetimes.co.uk/', 'https://www.dailyexpress.co.uk/', 'https://www.mirror.co.uk/',
                'https://www.standard.co.uk/', 'https://www.cityam.com/', 'https://www.theweek.co.uk/',
                'https://www.prospectmagazine.co.uk/', 'https://www.newstatesman.com/', 'https://www.townandcountrymag.com/',
                'https://www.countrylife.co.uk/', 'https://www.period.co.uk/', 'https://www.gq-magazine.co.uk/',
                'https://www.vogue.co.uk/', 'https://www.harperbazaarcollections.co.uk/', 'https://www.cosmopolitan.co.uk/',
                'https://www.marieclaire.co.uk/', 'https://www.elitedaily.com/', 'https://www.refinery29.com/',
                'https://www.buzzfeed.com/', 'https://www.huffingtonpost.co.uk/', 'https://www.vice.com/',
                'https://www.rollingstone.com/', 'https://www.variety.com/', 'https://www.hollywoodreporter.com/'
            ]
        }

    def generar_whitelist(self, pais_seleccionado, cantidad):
        """Genera la whitelist según país y cantidad"""
        if pais_seleccionado not in self.medios_confiables:
            return []
        
        urls = self.medios_confiables[pais_seleccionado]
        
        # Ajustar cantidad
        if cantidad > len(urls):
            # Repetir URLs si se necesita más cantidad
            urls_extendidas = []
            while len(urls_extendidas) < cantidad:
                urls_extendidas.extend(urls)
            urls = urls_extendidas[:cantidad]
        else:
            urls = urls[:cantidad]
        
        return urls

# Instancia global del generador
generator = WhitelistGenerator()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generador de Whitelist de Medios</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-weight: normal;
        }
        .form-group {
            margin: 20px 0;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #3498db;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        .btn {
            background: linear-gradient(to right, #3498db, #2980b9);
            color: white;
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            margin: 10px 5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }
        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
        }
        .btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .progress-container {
            margin: 20px 0;
            display: none;
        }
        .progress-bar {
            width: 100%;
            height: 24px;
            background-color: #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(to right, #2ecc71, #27ae60);
            width: 0%;
            transition: width 0.4s ease;
            border-radius: 12px;
        }
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        .status {
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .result-link {
            display: none;
            margin-top: 25px;
            text-align: center;
        }
        .instructions {
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #17a2b8;
        }
        .instructions h3 {
            margin-top: 0;
            color: #17a2b8;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Generador de Whitelist de Medios</h1>
        <p class="subtitle">Selecciona país y cantidad de sitios para generar tu archivo Excel</p>
        
        <div class="instructions">
            <h3>📋 Instrucciones:</h3>
            <ul>
                <li>Selecciona el país del cual deseas obtener sitios web</li>
                <li>Indica la cantidad de sitios que deseas (máximo 1000 por defecto)</li>
                <li>Haz clic en "Generar Excel" para crear el archivo</li>
                <li>Descarga el archivo Excel generado con los sitios seleccionados</li>
            </ul>
        </div>
        
        <div class="form-group">
            <label for="pais"> País:</label>
            <select id="pais" name="pais">
                <option value="">Seleccione un país</option>
                <option value="Brasil">Brasil</option>
                <option value="Perú">Perú</option>
                <option value="Argentina">Argentina</option>
                <option value="Uruguay">Uruguay</option>
                <option value="Suiza">Suiza</option>
                <option value="Bélgica">Bélgica</option>
                <option value="Portugal">Portugal</option>
                <option value="Holanda">Holanda</option>
                <option value="Reino Unido">Reino Unido</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="cantidad">Cantidad de sitios (máximo 1000):</label>
            <input type="number" id="cantidad" name="cantidad" min="1" max="1000" value="100">
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn" onclick="generarExcel()" id="generarBtn">
                <span id="btnText">📊 Generar Excel</span>
                <span id="btnLoading" class="loading" style="display: none;"></span>
            </button>
        </div>
        
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
                <div class="progress-text" id="progressText">0%</div>
            </div>
        </div>
        
        <div class="status" id="status"></div>
        
        <div class="result-link" id="resultLink">
            <h3>🎉 Archivo generado exitosamente!</h3>
            <p>Tu archivo Excel con la whitelist está listo para descargar:</p>
            <a id="downloadLink" class="btn" href="#" download>
                <span>📥 Descargar Whitelist</span>
            </a>
        </div>
    </div>

    <script>
        function generarExcel() {
            const pais = document.getElementById('pais').value;
            const cantidad = parseInt(document.getElementById('cantidad').value);
            
            if (!pais) {
                showStatus('Por favor selecciona un país', 'error');
                return;
            }
            
            if (!cantidad || cantidad < 1 || cantidad > 1000) {
                showStatus('Por favor ingresa una cantidad válida entre 1 y 1000', 'error');
                return;
            }
            
            // Actualizar UI
            const btn = document.getElementById('generarBtn');
            const btnText = document.getElementById('btnText');
            const btnLoading = document.getElementById('btnLoading');
            
            btn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline-block';
            
            // Mostrar barra de progreso
            document.getElementById('progressContainer').style.display = 'block';
            resetProgress();
            
            // Llamar al endpoint para generar el archivo
            fetch(`/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pais: pais,
                    cantidad: cantidad
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.blob();
            })
            .then(blob => {
                // Crear URL para el blob
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `whitelist_${pais.replace(' ', '_')}_${cantidad}_sites.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                updateProgress(100);
                showStatus('Archivo descargado exitosamente!', 'success');
                
                // Restaurar botón
                btn.disabled = false;
                btnText.style.display = 'inline';
                btnLoading.style.display = 'none';
            })
            .catch(error => {
                console.error('Error:', error);
                showStatus('Error al generar el archivo: ' + error.message, 'error');
                
                // Restaurar botón
                btn.disabled = false;
                btnText.style.display = 'inline';
                btnLoading.style.display = 'none';
            });
        }
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<strong>${type === 'success' ? '✅' : '❌'}</strong> ${message}`;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
            
            // Scroll hacia el mensaje
            statusDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        function resetProgress() {
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressText').textContent = '0%';
        }
        
        function updateProgress(percentage) {
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            progressFill.style.width = `${percentage}%`;
            progressText.textContent = `${Math.round(percentage)}%`;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.get_json()
        pais = data.get('pais', '')
        cantidad = data.get('cantidad', 100)
        
        if not pais:
            return jsonify({'success': False, 'error': 'País no especificado'}), 400
        
        cantidad = min(int(cantidad), 1000)  # Limitar a 1000 como máximo
        
        # Generar la whitelist
        urls = generator.generar_whitelist(pais, cantidad)
        
        # Crear DataFrame
        df = pd.DataFrame({'URL': urls})
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=pais, index=False)
        
        output.seek(0)
        
        # Devolver archivo para descarga
        filename = f"whitelist_{pais.replace(' ', '_')}_{cantidad}_sites.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
