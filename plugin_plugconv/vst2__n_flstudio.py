# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import base64
import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import data_values
from functions import plugin_vst2
from functions import plugins

from functions_plugparams import params_various_inst
from functions_plugparams import params_kickmess
from functions_plugparams import params_various_fx
from functions_plugparams import params_vital
from functions_plugparams import wave
from functions_plugparams import data_nullbytegroup

simsynth_shapes = {0.4: 'noise', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}

def simsynth_time(value): return pow(value*2, 3)
def simsynth_2time(value): return pow(value*2, 3)

def getparam(paramname):
    global pluginid_g
    global cvpj_l_g
    paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
    return paramval[0]

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-flstudio', None, 'flp'], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        global pluginid_g
        global cvpj_l_g
        pluginid_g = pluginid
        cvpj_l_g = cvpj_l

        #---------------------------------------- Fruit Kick ----------------------------------------
        if plugintype[1].lower() == 'fruit kick':
            print('[plug-conv] Converting Fruit Kick to Kickmess:',pluginid)
            max_freq = note_data.note_to_freq((getparam('max_freq')/100)+12) #1000
            min_freq = note_data.note_to_freq((getparam('min_freq')/100)-36) #130.8128
            decay_freq = getparam('decay_freq')/256
            decay_vol = getparam('decay_vol')/256
            osc_click = getparam('osc_click')/64
            osc_dist = getparam('osc_dist')/128
            #print(fkp, max_freq, min_freq, decay_freq, decay_vol, osc_click, osc_dist  )
            params_kickmess.initparams()
            params_kickmess.setvalue('pub', 'freq_start', max_freq)
            params_kickmess.setvalue('pub', 'freq_end', min_freq)
            params_kickmess.setvalue('pub', 'env_slope', decay_vol)
            params_kickmess.setvalue('pub', 'freq_slope', 0.5)
            params_kickmess.setvalue('pub', 'f_env_release', decay_freq*150)
            params_kickmess.setvalue('pub', 'phase_offs', osc_click)
            if osc_dist != 0:
                params_kickmess.setvalue('pub', 'dist_on', 1)
                params_kickmess.setvalue('pub', 'dist_start', osc_dist*0.1)
                params_kickmess.setvalue('pub', 'dist_end', osc_dist*0.1)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'Kickmess (VST)', 'chunk', params_kickmess.getparams(), None)
            plugins.add_plug_data(cvpj_l, pluginid, 'middlenotefix', -12)
            return True

        # ---------------------------------------- DX10 ----------------------------------------
        elif plugintype[1].lower() == 'fruity dx10':
            print('[plug-conv] Converting Fruity DX10 to mda DX10:',pluginid)
            param_amp_att = getparam('amp_att')/65536
            param_amp_dec = getparam('amp_dec')/65536
            param_amp_rel = getparam('amp_rel')/65536
            param_mod_course = getparam('mod_course')/65536
            param_mod_fine = getparam('mod_fine')/65536
            param_mod_init = getparam('mod_init')/65536
            param_mod_time = getparam('mod_time')/65536
            param_mod_sus = getparam('mod_sus')/65536
            param_mod_rel = getparam('mod_rel')/65536
            param_velsen = getparam('velsen')/65536
            param_vibrato = getparam('vibrato')/65536
            param_octave = (getparam('octave')+2)/5
            param_waveform = getparam('waveform')/65536
            param_mod_thru = getparam('mod_thru')/65536
            param_lforate = getparam('lforate')/65536

            plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'DX10', 'param', None, 16)
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', param_amp_att, 'float', "Attack  ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', param_amp_dec, 'float', "Decay   ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_2', param_amp_rel, 'float', "Release ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_3', param_mod_course, 'float', "Coarse  ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_4', param_mod_fine, 'float', "Fine    ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_5', param_mod_init, 'float', "Mod Init", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_6', param_mod_time, 'float', "Mod Dec ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_7', param_mod_sus, 'float', "Mod Sus ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_8', param_mod_rel, 'float', "Mod Rel ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_9', param_velsen, 'float', "Mod Vel ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_10', param_vibrato, 'float', "Vibrato ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_11', param_octave, 'float', "Octave  ", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_12', 0.5, 'float', "FineTune", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_13', param_waveform, 'float', "Waveform", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_14', param_mod_thru, 'float', "Mod Thru", )
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_15', param_lforate, 'float', "LFO Rate", )
            return True

        # ---------------------------------------- SimSynth ----------------------------------------
        elif plugintype[1].lower() == 'simsynth':
            print('[plug-conv] Converting SimSynth to Vital:',pluginid)
            params_vital.create()

            for oscnum in range(3):
                starttextparam = 'osc'+str(oscnum+1)
                starttextparam_vital = 'osc_'+str(oscnum+1)
                osc_shape = getparam(starttextparam+'_shape')
                osc_pw = getparam(starttextparam+'_pw')
                osc_o1 = int(getparam(starttextparam+'_o1'))
                osc_o2 = int(getparam(starttextparam+'_o2'))
                osc_on = float(getparam(starttextparam+'_on'))
                osc_crs = getparam(starttextparam+'_crs')
                osc_fine = getparam(starttextparam+'_fine')
                osc_lvl = getparam(starttextparam+'_lvl')
                osc_warm = int(getparam(starttextparam+'_warm'))

                vital_osc_shape = []
                for num in range(2048): 
                    vital_osc_shape.append(
                        wave.tripleoct(num/2048, simsynth_shapes[osc_shape], osc_pw, osc_o1, osc_o2)
                        )
                params_vital.replacewave(oscnum, vital_osc_shape)
                params_vital.setvalue(starttextparam_vital+'_on', osc_on)
                params_vital.setvalue(starttextparam_vital+'_transpose', (osc_crs-0.5)*48)
                params_vital.setvalue(starttextparam_vital+'_tune', (osc_fine-0.5)*2)
                params_vital.setvalue(starttextparam_vital+'_level', osc_lvl)
                if osc_warm == 1:
                    params_vital.setvalue(starttextparam_vital+'_unison_detune', 2.2)
                    params_vital.setvalue(starttextparam_vital+'_unison_voices', 6)

            # ------------ AMP ------------
            params_vital.setvalue_timed('env_1_attack', simsynth_time(getparam('amp_att'))*3.5)
            params_vital.setvalue_timed('env_1_decay', simsynth_2time(getparam('amp_dec'))*3.5)
            params_vital.setvalue('env_1_sustain', getparam('amp_sus'))
            params_vital.setvalue_timed('env_1_release', simsynth_2time(getparam('amp_rel'))*3.5)

            # ------------ SVF ------------
            params_vital.setvalue_timed('env_2_attack', simsynth_time(getparam('svf_att'))*7)
            params_vital.setvalue_timed('env_2_decay', simsynth_2time(getparam('svf_dec'))*7)
            params_vital.setvalue('env_2_sustain', getparam('svf_sus'))
            params_vital.setvalue_timed('env_2_release', simsynth_2time(getparam('svf_rel'))*7)

            outfilter = 100
            outfilter += (getparam('svf_cut')-0.5)*40
            outfilter += (getparam('svf_kb')-0.5)*10

            params_vital.setvalue('filter_fx_resonance', getparam('svf_emph')*0.8)
            params_vital.setvalue('filter_fx_cutoff', outfilter)
            params_vital.setvalue('filter_fx_on', 1)
            params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', getparam('svf_env')*0.6, 0, 0, 0, 0)

            # ------------ Chorus ------------
            params_vital.setvalue('chorus_mod_depth', 0.35)
            params_vital.setvalue('chorus_delay_1', -9.5)
            params_vital.setvalue('chorus_delay_2', -9.0)
            if getparam('chorus_on') == True: params_vital.setvalue('chorus_on', 1.0)
            
            vitaldata = params_vital.getdata()
            plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)
            return True

        elif plugintype[1].lower() == 'fruity bass boost':
            print('[plug-conv] Converting Fruity Bass Boost to Airwindows Weight:',pluginid)
            param_freq = (getparam('freq')/1024)*0.8
            param_amount = (getparam('amount')/1024)*0.8
            plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'Weight', 'param', None, 2)
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', param_freq, 'float', "Freq")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', param_amount, 'float', "Weight")
            return True

        elif plugintype[1].lower() == 'fruity phaser':
            print('[plug-conv] Converting Fruity Phaser to SupaPhaser:',pluginid)
            param_sweep_freq = getparam('sweep_freq')/5000
            param_depth_min = getparam('depth_min')/1000
            param_depth_max = getparam('depth_max')/1000
            param_freq_range = getparam('freq_range')/1024
            param_stereo = getparam('stereo')/1024
            param_num_stages = getparam('num_stages')/22
            param_feedback = getparam('feedback')/1000
            param_drywet = getparam('drywet')/1024
            param_gain = getparam('gain')/5000
            plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'SupaPhaser', 'param', None, 16)
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', 0, 'float', "attack")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', 0, 'float', "release")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_2', 0, 'float', "min env")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_3', 0, 'float', "max env")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_4', 0, 'float', "env-lfo mixture")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_5', param_sweep_freq, 'float', "sweep freq.")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_6', param_depth_min, 'float', "min. depth")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_7', param_depth_max, 'float', "max. depth")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_8', param_freq_range, 'float', "freq. range")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_9', param_stereo, 'float', "stereo")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_10', param_num_stages, 'float', "nr. stages")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_11', 0, 'float', "distortion")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_12', param_feedback, 'float', "feedback")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_13', param_drywet, 'float', "dry-wet")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_14', param_gain, 'float', "out gain")
            plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_15', 0, 'float', "invert")
            return True

        elif plugintype[1].lower() == 'fruity spectroman':
            print("[plug-conv] Converting Fruity Spectroman to Socalab's SpectrumAnalyzer:",pluginid)
            spectroman_mode = getparam('outputmode')
            x_spectrumanalyzer = ET.Element("state")
            x_spectrumanalyzer.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state width="400" height="328"/>')
            x_spectrumanalyzer.set('program', '0')
            params_various_inst.socalabs_addparam(x_spectrumanalyzer, "mode", float(spectroman_mode))
            params_various_inst.socalabs_addparam(x_spectrumanalyzer, "log", 1.0)
            plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'SpectrumAnalyzer', 'chunk', ET.tostring(x_spectrumanalyzer, encoding='utf-8'), None)
            return True

        if plugintype[1].lower() == 'fruity waveshaper':
            print('[plug-conv] Converting Fruity Waveshaper to Wolf Shaper:',pluginid)
            params_various_fx.wolfshaper_init()
            params_various_fx.wolfshaper_setvalue('pregain', ((getparam('preamp')/128)-0.5)*2)
            params_various_fx.wolfshaper_setvalue('wet', getparam('wet')/128)
            params_various_fx.wolfshaper_setvalue('postgain', getparam('postgain')/128)
            params_various_fx.wolfshaper_setvalue('bipolarmode', float(getparam('bipolarmode')))
            params_various_fx.wolfshaper_setvalue('removedc', float(getparam('removedc')))

            shapeenv = plugins.get_env_points(cvpj_l, pluginid, 'shape')
            if shapeenv != None:
                params_various_fx.wolfshaper_addshape(shapeenv)

            plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'Wolf Shaper', 'chunk', data_nullbytegroup.make(params_various_fx.wolfshaper_get()), None)
            return True