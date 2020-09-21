import pysam
import numpy as np
import os
import shutil
import random

from hmmtuf import ENABLE_SPADE, SPADE_PATH

from . constants import INFO, WARNING
from . constants import TREAT_ERRORS_AS_WARNINGS

fas = None
outbedgraph = None
outtuf = None
outnor = None
outdel = None
outdup = None
outgap = None
outtdt = None
outquad = None
outrep = None
quadout = None
nucl_out = None

PATH = None
SPADE_OUTPATH = None


# this function copied from gquadfinder
def BaseScore(line):

    item, liste=0, []

    while item < len(line):
        if item < len(line) and (line[item] == "G" or line[item] == "g"):
            liste.append(1)
            if item+1 < len(line) and (line[item+1] == "G" or line[item+1] == "g"):
                liste[item]=2
                liste.append(2)
                if item+2< len(line) and (line[item+2] == "G" or line[item+2] == "g"):
                    liste[item+1] = 3
                    liste[item] = 3
                    liste.append(3)
                    if item+3 < len(line) and (line[item+3] == "G" or line[item+3] == "g"):
                        liste[item] = 4
                        liste[item+1] = 4
                        liste[item+2] = 4
                        liste.append(4)
                        item = item+1
                    item = item+1
                item = item+1
            item = item+1
            while item < len(line) and (line[item] == "G" or line[item] == "g"):
                    liste.append(4)
                    item = item+1
    
        elif item < len(line) and line[item] != "G" and line[item] != "g" and line[item] != "C" and line[item] != "c":
                    liste.append(0)
                    item = item+1
            
        elif item < len(line) and (line[item] == "C" or line[item] == "c"):
            liste.append(-1)
            if item+1 < len(line) and (line[item+1] == "C" or line[item+1] == "c"):
                liste[item] = -2
                liste.append(-2)
                if item+2 < len(line) and (line[item+2] == "C" or line[item+2] == "c"):
                    liste[item+1]=-3
                    liste[item]=-3
                    liste.append(-3)
                    if item+3 < len(line) and (line[item+3] == "C" or line[item+3] == "c"):
                        liste[item] = -4
                        liste[item+1] = -4
                        liste[item+2] = -4
                        liste.append(-4)
                        item = item+1
                    item = item+1
                item = item+1
            item = item+1

            while item < len(line) and (line[item] == "C" or line[item] == "c"):
                liste.append(-4)
                item = item+1
        
        else:
                # la fin du la ligne ou y a des entrers
                item = item+1
    return line, liste


# this function copied from gquadfinder
def CalScore(liste, k):

    Score_Liste=[]
    for i in range(len(liste)-(k-1)):
        j, Sum = 0, 0

        while j < k:
            Sum = Sum + liste[i]
            j = j + 1
            i = i + 1
        Mean=Sum/float(k)
        Score_Liste.append(Mean) 
    return Score_Liste

# this function copied from gquadfinder
def GetG4(line, liste, Window, k, Len):

    LG4 = []
    for i in range(len(liste)):
        if liste[i] >= float(Window) or liste[i] <= - float(Window):
            seq = line[i:i+k]
            LG4.append(i)
    return LG4


# this function copied from gquadfinder
def WriteSeq(line,liste, LISTE, F, Len ):

    i,k,I=0,0,0
    a=b=LISTE[i]
    MSCORE=[]

    if len(LISTE) > 1:
        c = LISTE[i+1]
        while i < len(LISTE)-2:
            if c == b+1:
                k = k+1
                i = i+1
            else:
                I = I+1
                seq = line[a:a+F+k]
                sequence, liste2 = BaseScore(seq)
                MSCORE.append(abs(round(np.mean(liste2), 2)))
                k = 0
                i = i+1
                a = LISTE[i]
            b = LISTE[i]
            c = LISTE[i+1]
        I=I+1
        seq=line[a:a+F+k+1]
        sequence, liste2 = BaseScore(seq)
        MSCORE.append(abs(round(np.mean(liste2), 2)))
    else:
        I = I+1
        seq = line[a:a+F]
        MSCORE.append(abs(liste[a]))
    return MSCORE   


# this function copied from gquadfinder
def gquadcheck(sequence):

    minscore = 2
    window = 50

    cseq, scores = BaseScore(sequence)
    score = CalScore(scores, window)
    outG4 = GetG4(sequence, score, minscore, window, len(scores))

    if len(outG4) == 0:
        return False, []

    mscore = WriteSeq(sequence, score, outG4, window, len(scores))

    if len(mscore):
        return True, mscore
    else:
        return False, mscore


def match(win, altwin):
    m = 0
    for a,b in zip (win,altwin):
        if a == b:
            m += 1
    if m > 8:
        return True
    else:
        return False


def gcpercent(cseq):
    """
    Calculate GC percent from the sequence
    """

    count = 0
    count += cseq.count('G')
    count += cseq.count('g')
    count += cseq.count('C')
    count += cseq.count('c')
    count = str(int(count/len(cseq)*100))
    return count


def spade(repseq, chrom, start, stop, type):

    """
    Call SPADE application in the SPADE_PATH
    """

    global outrep
    global nucl_out

    global PATH
    global SPADE_OUTPATH

    if outrep is None:
        raise Exception("outrep file is None")

    if nucl_out is None:
        raise Exception("nucl_out file is None")

    if PATH is None:
        raise Exception("PATH variable not specified")

    if SPADE_OUTPATH is None:
        raise Exception("SPADE_OUTPATH variable not specified")

    if not os.path.isdir(PATH + 'repeats'):
        try:
            os.mkdir(PATH + 'repeats')
        except OSError as e:

            if TREAT_ERRORS_AS_WARNINGS:
                print("%s Error: %s." % (WARNING, e.strerror))
            else:
                raise e

    fasta = open(PATH + 'repeats/tdtseq.fasta', 'w')

    folder = chrom + '_'+str(start) + '-' + str(stop) + '_' + type + '_' + gcpercent(repseq)

    fasta.write('>'+folder+'\n')
    fasta.write(repseq+'\n')
    fasta.close()
    str_cmd = 'python3 {0} -in {1} -out_dir {2}'.format(SPADE_PATH + 'SPADE.py',
                                                        PATH + 'repeats/tdtseq.fasta',
                                                        SPADE_OUTPATH)
    print("{0} str_cmd {1}".format(INFO, str_cmd))
    os.system(str_cmd)

    # open the nucl files and attempt to write the
    # outrep file
    directories = os.listdir(path=SPADE_OUTPATH)

    for name in directories:

        # if this is a nucl_ directory
        if name.startswith('nucl_'):

            files = os.listdir(path=SPADE_OUTPATH + name)
            if 'weblogo.txt' in files:

                nucleods = ['A', 'C', 'G', 'T']
                count = 0
                with open(SPADE_OUTPATH + name + '/' + 'weblogo.txt', 'r') as f:
                    for line in f:
                        count += 1

                        # don't process the comment line
                        if line.startswith('#'):
                            continue

                        # checkout from the line which has the maximum
                        new_line = line.split('\t')

                        if len(new_line) > 5:
                            new_line = new_line[1:5]
                            new_line = [int(item) for item in new_line]
                            max_item = max(new_line)
                            nucleod_idx = new_line.index(max_item)

                            if nucleod_idx >= 4:
                                raise ValueError("Invalid index for nucleod. "
                                                 "Index {0} not in [0,3]".format(nucleod_idx))

                            nucleod = nucleods[nucleod_idx]
                            nucl_out.write(chrom + '\t' + str(start) + '\t' + str(stop) + '\t' + nucleod + '\n')

                # TODO: Make this application defined?
                if count > 12:
                    outrep.write(chrom + '\t' + str(start) + '\t' + str(stop) + '\n')


def createbed(line, ccheck):

    data = {}
    line = line.split(':')
    if len(line) == 5:
        data['chr'] = line[0]
        data['loc'] = line[2]
        data['means'] = line[3]
        data['state'] = line[4].rstrip()
        data['loc'] = data['loc'].replace('(', '')
        data['loc'] = data['loc'].replace(')', '')
        data['loc'] = data['loc'].split(',')
    elif len(line) == 4:
        data['chr'] = ccheck
        data['loc'] = line[1]
        data['means'] = line[2]
        data['state'] = line[3].rstrip()
        data['loc'] = data['loc'].replace('(', '')
        data['loc'] = data['loc'].replace(')', '')
        data['loc'] = data['loc'].split(',')             
    elif len(line) == 1:
        print("{0} start of file".format(INFO))
    else:
        print("{0} incorrect format of viterbi".format(INFO))
    return data


def doTDT(tdtarray, outfile):

    global outtdt
    global outquad
    global fas

    if outgap is None:
        raise Exception("outquad file is None")

    if outtdt is None:
        raise Exception("outtdt file is None")

    if fas is None:
        raise Exception("fas file is None")

    for tdt in tdtarray:
        # check not a deletion beginning
        # do quad and repeat finding
        # print(tdt)
        seq = fas.fetch(tdt['chr'], tdt['start'], tdt['end'])
        if ENABLE_SPADE:
            spade(seq, tdt['chr'], tdt['start'], tdt['end'], tdt['type'])

        if tdt['type'] == 'Deletion' and len(seq) < 2000:
            outtdt.write(tdt['chr'] + '\t' +
                         str(tdt['start']) + '\t' +
                         str(tdt['end']) + '\n')

        gquad, mscore = gquadcheck(seq)

        if gquad:
            outquad.write(tdt['chr']+'\t'+str(tdt['start'])+'\t'+str(tdt['end'])+'\n')
        outfile.write(tdt['chr'] + ':' + str(tdt['start']) +
                      '-' + str(tdt['end']) + '_' + tdt['type'] +
                      '_' + gcpercent(seq) + '\t' + str(gquad) + str(mscore) + '\n')


def remove_directories(chromosome):

    global SPADE_OUTPATH
    directories = os.listdir(path=SPADE_OUTPATH)

    for name in directories:

        # remove gb files
        if name.endswith('gb'):
            os.remove(os.path.join(SPADE_OUTPATH, name))

        if name.startswith(chromosome + '_'):
            if os.path.isdir(SPADE_OUTPATH + name):
                shutil.rmtree(os.path.join(SPADE_OUTPATH, name))
        # if this is a nucl_ directory
        if name.startswith('nucl_'):
            files = os.listdir(path=SPADE_OUTPATH + name)

            for f in files:
                if f != 'weblogo.txt':
                    os.remove(os.path.join(SPADE_OUTPATH + name, f))


def main(path, fas_file_name, chromosome,
         chr_idx, viterbi_file, remove_dirs=False):

    print("{0} Start TUF-DEL-TUF".format(INFO))

    global fas
    global outbedgraph
    global outtuf
    global outnor
    global outdel
    global outdup
    global outgap
    global outtdt
    global outquad
    global outrep
    global quadout
    global nucl_out

    global PATH
    global SPADE_OUTPATH

    PATH = path

    if ENABLE_SPADE:
        os.mkdir(PATH + "repeats")
        os.mkdir(PATH + "spade_output")
        SPADE_OUTPATH = PATH + "spade_output/"

    # read global reference file
    fas = pysam.FastaFile(fas_file_name)

    # TODO: these should be set by the application
    conv = {'TUF': 10,
            'TUFDUP': 12,
            'Normal-I': 40,
            'Normal-II': 42,
            'Deletion': 30,
            'Duplication': 50,
            'GAP_STATE': 0}

    files_created = ["viterbi.bedgraph",
                     "tuf.bed",
                     "normal.bed",
                     "deletion.bed",
                     "duplication.bed",
                     "gap.bed",
                     "tdt.bed", "quad.bed",
                     "rep.bed", 'gquads.txt',
                     "nucl_out.bed"]

    # Open global files
    outbedgraph = open(path + "viterbi.bedgraph", "w")
    outtuf = open(path + "tuf.bed", "w")
    outnor = open(path + "normal.bed", "w")
    outdel = open(path + "deletion.bed", "w")
    outdup = open(path + "duplication.bed", "w")
    outgap = open(path + "gap.bed", "w")
    outtdt = open(path + "tdt.bed", "w")
    outquad = open(path + "quad.bed", "w")
    outrep = open(path + "rep.bed", "w")
    quadout = open(path + 'gquads.txt', 'w')
    nucl_out = open(path + 'nucl_out.bed', 'w')

    prevstate = ""
    start = 0
    end = 0
    chr = ''
    ptemp = True
    chrlistsorted = {chr_idx: viterbi_file}

    for i in sorted(chrlistsorted):

        flist = []
        viterbisorted = chrlistsorted

        for f in flist:
            # if 'tuf_delete_tuf' in f and '._' not in f:
            #     tdtsorted[int(f.split('_')[6])] = f
            if 'viterbi' in f and '._' not in f:
                viterbisorted[int(f.split('_')[5])] = f

        tdtcheck = ''
        tdtlist = []

        for j in sorted(viterbisorted):
            print("{0} working with file: {1}".format(INFO, viterbisorted[j]))
            with open(viterbisorted[j]) as vfile:

                ccheck = chrlistsorted[i].split('_')[2].rstrip()

                for line in vfile:
                    vdata = createbed(line, ccheck)

                    if len(vdata) == 0:
                        continue

                    outbedgraph.write(vdata['chr']+'\t' + str(int(float(vdata['loc'][0]))) +
                                      '\t'+str(int(float(vdata['loc'][1]))) + '\t'+str(conv[vdata['state']])+'\n')
                    curstate = vdata['state']

                    if curstate == 'TUFDUP':
                        curstate = 'TUF'
                    elif curstate == 'Normal-II':
                        curstate = 'Normal-I'
                    if prevstate == "":
                        prevstate = curstate
                        chr = vdata['chr']
                        start = int(float(vdata['loc'][0]))
                        end = int(float(vdata['loc'][1]))
                    if curstate == prevstate and chr == vdata['chr'] and (int(float(vdata['loc'][0])) == end+1 or ptemp):
                        end = int(float(vdata['loc'][1]))
                    if curstate != prevstate or chr != vdata['chr'] or (int(float(vdata['loc'][0])) != end+1 and not ptemp):
                        if prevstate == 'TUF':
                            tdtcheck = tdtcheck + 'T'
                            tdtlist.append({"chr": chr, "start": start, "end": end, "type": 'TUF'})
                            print(chr+'\t'+str(start)+'\t'+str(end)+'TUF')
                            outtuf.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')
                        if prevstate == 'Normal-I':
                            if 'TDT' in tdtcheck:
                                print("{0} Processing TDT file".format(INFO))
                                doTDT(tdtlist, quadout)
                                print("{0} Done Processing TDT file".format(INFO))

                            tdtcheck = ''
                            tdtlist = []
                            print("{0} {1}".format(INFO, chr+'\t'+str(start)+'\t'+str(end)+'Normal'))
                            outnor.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')
                            if (end-start) > 1000:
                                p = random.randint(1,10)
                                print("{0} normal >1000, rand: {1}".format(INFO, p))
                                if p == 7:
                                    print("{0} processing random 1000 from normal region".format(INFO))
                                    n = random.randint(start, end-1000)
                                    nseq = fas.fetch(chr, n, n+1000)
                                    # print("calculating random normal G Quad")
                                    gquad, mscore = gquadcheck(nseq)
                                    quadout.write(chr + ':' + str(n) + '-'+str(n+1000) + '_' +
                                                  'Normal' + '_'+gcpercent(nseq) + '\t' +
                                                  str(gquad)+str(mscore)+'\n')

                                    if ENABLE_SPADE:
                                        spade(nseq, chr, n, n+1000, 'Normal')
                            else:
                                print("{0} normal too short".format(INFO))
                        if prevstate == 'Deletion':
                            if len(tdtcheck) > 0 and tdtcheck[0] == 'T':
                                tdtcheck = tdtcheck+'D'
                                tdtlist.append({"chr": chr, "start": start, "end": end, "type": 'Deletion'})

                            print("{0} {1}".format(INFO, chr+'\t'+str(start)+'\t'+str(end)+'Deletion'))
                            outdel.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')
                        if prevstate == 'Duplication':
                            if 'TDT' in tdtcheck:
                                print("{0} Processing TDT file".format(INFO))
                                doTDT(tdtlist, quadout)
                                print("{0} Done Processing TDT file".format(INFO))
                            tdtcheck = ''
                            tdtlist = []
                            print(chr+'\t'+str(start)+'\t'+str(end)+'Duplication')
                            outdup.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')
                        if prevstate == 'GAP_STATE':
                            if 'TDT' in tdtcheck:
                                print("{0} Processing TDT file".format(INFO))
                                doTDT(tdtlist, quadout)
                                print("{0} Done Processing TDT file".format(INFO))
                            tdtcheck = ''
                            tdtlist = []
                            print(chr+'\t'+str(start)+'\t'+str(end)+'GAP')
                            outgap.write(chr+'\t'+str(start)+'\t'+str(end)+'\n')
                        chr = vdata['chr']
                        start = int(float(vdata['loc'][0]))
                        end = int(float(vdata['loc'][1]))
                        prevstate = curstate

    quadout.close()
    outbedgraph.close()
    outtuf.close()
    outnor.close()
    outdel.close()
    outdup.close()
    outgap.close()
    outtdt.close()
    outquad.close()
    outrep.close()
    nucl_out.close()

    if remove_dirs:
        remove_directories(chromosome=chromosome)

    print("{0} END TUF-DEL-TUF".format(INFO))
    return files_created


def concatenate_bed_files(bedfiles, outfile):

    with open(outfile, 'w') as total_f:
        for file_name in bedfiles:
            with open(file_name, 'r') as f:

                for line in f:
                    total_f.write(line)

            


