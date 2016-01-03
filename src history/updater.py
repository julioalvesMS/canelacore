#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, zipfile, os, shutil
import wx, json, threading

Main_url = "http://arkhamdeposit.xpg.uol.com.br/projects/canela/"
currentVersion = '1.5.0'


class UpdateAvaliable(wx.Dialog):
    def __init__(self, parent, intel):
        message = u"Nova atualização disponivel!\nVersão atual: %s       Nova versão: %s\nInstalar atualização?" %(currentVersion, intel["version"])
        self.intel = intel
        self.parent = parent
        wx.Dialog.__init__(self, parent, title=u"Atualização", size = (-1, 150), style = wx.CLOSE_BOX|wx.CAPTION)
        self.Centre()
        wx.StaticText(self, -1, message, pos=(10, 20))
        size = self.GetSize()
        yes = wx.Button(self, -1, u'Atualizar', pos=(size[0]/16, size[1]-65))
        no = wx.Button(self, -1, u'Agora não', pos=(size[0]/8 + size[0]/4, size[1]-65))
        helpb = wx.Button(self, -1, u'Novidades', pos=(3*size[0]/16 + size[0]/2, size[1]-65))
        helpb.Bind(wx.EVT_BUTTON, self.WhatsNew)
        yes.Bind(wx.EVT_BUTTON, self.ContinueUpdate)
        no.Bind(wx.EVT_BUTTON, self.NotNow)
        self.ShowModal()

    def WhatsNew(self, event):
        os.system('start ' + Main_url+self.intel["news"])

    def ContinueUpdate(self, event):
        dialog(self.intel)
        self.Destroy()

    def NotNow(self, event):
        self.Destroy()

def checkUpdate(parent=None, called=False):
    try:
        print 'connecting'
        request = urllib2.urlopen(Main_url)
        print 'connected'
        response = request.read()
        response = response[response.index('{"'):response.index(']}')+2]
        print 'read'

    except:
        if called:
            a = wx.MessageDialog(parent, u'Não foi possível procurar por atualizações', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
        return False
    intel = json.loads(response)
    if newer_version(intel["version"], currentVersion):
        print 'available'
        return intel
    return False

def newer_version(new, old):
    if new==old:
        return False
    x = new.split('.')
    y = old.split('.')
    l = min(len(x), len(y))
    for i in range(l):
        if int(x[i]) > int(y[i]):
            return True
        elif int(x[i]) < int(y[i]):
            return False
    if len(x)>len(y):
        return True

def dialog(intel):
    dlg = wx.ProgressDialog(u'Update Canela Core',
                            u'Atualizando Canela Core para a versão mais recente',
                            maximum=1001,
                            parent=None,
                            style=wx.PD_CAN_ABORT
                            | wx.PD_ELAPSED_TIME
                            | wx.PD_ESTIMATED_TIME
                            | wx.PD_REMAINING_TIME
                            | wx.PD_SMOOTH)
    dlg.Show()
    pie = threading.Thread(target=download, args=(intel, dlg))
    pie.daemon = True
    pie.start()

def download(intel, progress=None, i=0, folder='UpdateFiles'):
    if i >= (len(intel['direct_links_zip']) + len(intel['direct_links_exe'])):
        print 'banana ' + str(i)
        progress.Close()
        return#fazer mais coisas com a progressdialog
    try:
        if folder:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            os.mkdir(folder)
            folder += '\\'
    except Exception:
        download(intel, progress, i, folder)
        return
    try:
        print str(i) + 'a'
        if i < len(intel['direct_links_zip']):
            url = intel['direct_links_zip'][i]
        else:
            url = intel['direct_links_exe'][i-len(intel['direct_links_zip'])]
        print str(i) + 'a2'
        print url
        print 'wtf 1'
        file_name = url.split('/')[-1]
        print 'wtf 2'
        if 'dl=' in file_name:
            url = url.split('?')[0]
            file_name = file_name.split('?')[0]
        print 'wtf 3'
        file_path = folder + file_name
        req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
        print 'wtf 4'
        u = urllib2.urlopen(req)
        print str(i) + 'b'
        f = open(file_path, 'wb')
        meta = u.info()
        print str(i) + 'c'
        print meta
        file_size = int(meta.getheaders("Content-Length")[0])
        if progress:
            (keep, skip) = progress.Update(0, u"Baixando:\n%s\n%s kb" % (file_name, file_size/(1024)))
            if not keep:
                f.close()
                shutil.rmtree(folder)
                progress.Destroy()
                return

        file_size_dl = 0
        block_sz = 1024
        print str(i) + 'd'
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = file_size_dl * 1000 / file_size
            if progress:
                (keep, skip) = progress.Update(status)
                if not keep:
                    f.close()
                    shutil.rmtree(folder)
                    progress.Destroy()
                    return
        f.close()
        (keep, skip) = progress.Update(1000, u'Descompactando os arquivos')
        if not keep:
            shutil.rmtree(folder)
            progress.Destroy()
            return
        (place, unpacked) = Unzipper(file_path)
        (keep, skip) = progress.Update(1000, u'Transferindo os dados')
        if not keep:
            shutil.rmtree(folder)
            progress.Destroy()
            return
        FileTransfer(place + '\\' + unpacked[0][:-1])
        shutil.rmtree(folder)
        progress.Update(1001)

    except Exception, e:
        print 'aaaaaaaaaahaaa', e
        download(intel, progress, i+1, folder)
        return

def Unzipper(file, folder=-1):
    if file.split('.')[-1] == 'zip':
        if folder == -1:
            folders = os.path.realpath(os.curdir).split('\\')
            folder = '\\'.join(folders[:-1])
        else:
            folder = os.path.realpath(folder)
        compressed = zipfile.ZipFile(file, 'r')
        files = compressed.namelist()
        compressed.extractall(folder)
        compressed.close()
        return folder, files

def FileTransfer(newDir, curDir=-1):
    if curDir==-1:
        curDir = os.path.realpath(os.curdir)
    newDir = os.path.realpath(newDir)
    shutil.copytree('{0}\\saves'.format(curDir), newDir + '\\saves')
    shutil.copytree('{0}\\products'.format(curDir), newDir + '\\products')
    shutil.copytree('{0}\\clients'.format(curDir), newDir + '\\clients')
    shutil.copytree('{0}\\backup'.format(curDir), newDir + '\\backup')
    shutil.copytree('{0}\\preferences'.format(curDir), newDir + '\\preferences')
    if os.path.exists(curDir + '\\#Trash'):
        shutil.copytree('{0}\\#Trash'.format(curDir), newDir + '\\#Trash')

def main():
    intel = checkUpdate(None, True)
    if intel:
        g = wx.App()
        UpdateAvaliable(None, intel)
        g.MainLoop()

if __name__ == '__main__':
    main()