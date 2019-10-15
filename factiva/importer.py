from datetime import datetime
import logging
import os
from pprint import pprint
import re
import docx
import pandas as pd

from factiva import settings
from .models import Session, Articles, Company, CompanyArticle, db_engine, FileInfo


logger = logging.getLogger(__name__)


def striprtf(text):
    # Orignal function from https://gist.github.com/gilsondev/7c1d2d753ddb522e7bc22511cfb08676
    pattern = re.compile(r"\\([a-z]{1,32})(-?\d{1,10})?[ ]?|\\'([0-9a-f]{2})|\\([^a-z])|([{}])|[\r\n]+|(.)", re.I)
    # control words which specify a "destionation".
    destinations = frozenset((
        'aftncn', 'aftnsep', 'aftnsepc', 'annotation', 'atnauthor', 'atndate', 'atnicn', 'atnid',
        'atnparent', 'atnref', 'atntime', 'atrfend', 'atrfstart', 'author', 'background',
        'bkmkend', 'bkmkstart', 'blipuid', 'buptim', 'category', 'colorschememapping',
        'colortbl', 'comment', 'company', 'creatim', 'datafield', 'datastore', 'defchp', 'defpap',
        'do', 'doccomm', 'docvar', 'dptxbxtext', 'ebcend', 'ebcstart', 'factoidname', 'falt',
        'fchars', 'ffdeftext', 'ffentrymcr', 'ffexitmcr', 'ffformat', 'ffhelptext', 'ffl',
        'ffname', 'ffstattext', 'file', 'filetbl', 'fldtype',
        'fname', 'fontemb', 'fontfile', 'fonttbl', 'footer', 'footerf', 'footerl', 'footerr',
        'footnote', 'formfield', 'ftncn', 'ftnsep', 'ftnsepc', 'g', 'generator', 'gridtbl',
        'header', 'headerf', 'headerl', 'headerr', 'hl', 'hlfr', 'hlinkbase', 'hlloc', 'hlsrc',
        'hsv', 'htmltag', 'info', 'keycode', 'keywords', 'latentstyles', 'lchars', 'levelnumbers',
        'leveltext', 'lfolevel', 'linkval', 'list', 'listlevel', 'listname', 'listoverride',
        'listoverridetable', 'listpicture', 'liststylename', 'listtable', 'listtext',
        'lsdlockedexcept', 'macc', 'maccPr', 'mailmerge', 'maln', 'malnScr', 'manager', 'margPr',
        'mbar', 'mbarPr', 'mbaseJc', 'mbegChr', 'mborderBox', 'mborderBoxPr', 'mbox', 'mboxPr',
        'mchr', 'mcount', 'mctrlPr', 'md', 'mdeg', 'mdegHide', 'mden', 'mdiff', 'mdPr', 'me',
        'mendChr', 'meqArr', 'meqArrPr', 'mf', 'mfName', 'mfPr', 'mfunc', 'mfuncPr', 'mgroupChr',
        'mgroupChrPr', 'mgrow', 'mhideBot', 'mhideLeft', 'mhideRight', 'mhideTop', 'mhtmltag',
        'mlim', 'mlimloc', 'mlimlow', 'mlimlowPr', 'mlimupp', 'mlimuppPr', 'mm', 'mmaddfieldname',
        'mmath', 'mmathPict', 'mmathPr', 'mmaxdist', 'mmc', 'mmcJc', 'mmconnectstr',
        'mmconnectstrdata', 'mmcPr', 'mmcs', 'mmdatasource', 'mmheadersource', 'mmmailsubject',
        'mmodso', 'mmodsofilter', 'mmodsofldmpdata', 'mmodsomappedname', 'mmodsoname',
        'mmodsorecipdata', 'mmodsosort', 'mmodsosrc', 'mmodsotable', 'mmodsoudl',
        'mmodsoudldata', 'mmodsouniquetag', 'mmPr', 'mmquery', 'mmr', 'mnary', 'mnaryPr',
        'mnoBreak', 'mnum', 'mobjDist', 'moMath', 'moMathPara', 'moMathParaPr', 'mopEmu',
        'mphant', 'mphantPr', 'mplcHide', 'mpos', 'mr', 'mrad', 'mradPr', 'mrPr', 'msepChr',
        'mshow', 'mshp', 'msPre', 'msPrePr', 'msSub', 'msSubPr', 'msSubSup', 'msSubSupPr', 'msSup',
        'msSupPr', 'mstrikeBLTR', 'mstrikeH', 'mstrikeTLBR', 'mstrikeV', 'msub', 'msubHide',
        'msup', 'msupHide', 'mtransp', 'mtype', 'mvertJc', 'mvfmf', 'mvfml', 'mvtof', 'mvtol',
        'mzeroAsc', 'mzeroDesc', 'mzeroWid', 'nesttableprops', 'nextfile', 'nonesttables',
        'objalias', 'objclass', 'objdata', 'object', 'objname', 'objsect', 'objtime', 'oldcprops',
        'oldpprops', 'oldsprops', 'oldtprops', 'oleclsid', 'operator', 'panose', 'password',
        'passwordhash', 'pgp', 'pgptbl', 'picprop', 'pict', 'pn', 'pnseclvl', 'pntext', 'pntxta',
        'pntxtb', 'printim', 'private', 'propname', 'protend', 'protstart', 'protusertbl', 'pxe',
        'result', 'revtbl', 'revtim', 'rsidtbl', 'rxe', 'shp', 'shpgrp', 'shpinst',
        'shppict', 'shprslt', 'shptxt', 'sn', 'sp', 'staticval', 'stylesheet', 'subject', 'sv',
        'svb', 'tc', 'template', 'themedata', 'title', 'txe', 'ud', 'upr', 'userprops',
        'wgrffmtfilter', 'windowcaption', 'writereservation', 'writereservhash', 'xe', 'xform',
        'xmlattrname', 'xmlattrvalue', 'xmlclose', 'xmlname', 'xmlnstbl',
        'xmlopen',
    ))
    # Translation of some special characters.
    specialchars = {
        'par': '\n',
        'sect': '\n\n',
        'page': '\n\n',
        'line': '\n',
        'tab': '\t',
        'emdash': '\u2014',
        'endash': '\u2013',
        'emspace': '\u2003',
        'enspace': '\u2002',
        'qmspace': '\u2005',
        'bullet': '\u2022',
        'lquote': '\u2018',
        'rquote': '\u2019',
        'ldblquote': '\201C',
        'rdblquote': '\u201D',
        'trowd': '\n',
        'pard': "\t"
    }
    stack = []
    ignorable = False       # Whether this group (and all inside it) are "ignorable".
    ucskip = 1              # Number of ASCII characters to skip after a unicode character.
    curskip = 0             # Number of ASCII characters left to skip
    out = []                # Output buffer.
    for match in pattern.finditer(text):
        word, arg, hex, char, brace, tchar = match.groups()
        if brace:
            curskip = 0
            if brace == '{':
                # Push state
                stack.append((ucskip, ignorable))
            elif brace == '}':
                # Pop state
                ucskip, ignorable = stack.pop()
        elif char:  # \x (not a letter)
            curskip = 0
            if char == '~':
                if not ignorable:
                    out.append('\xA0')
            elif char in '{}\\':
                if not ignorable:
                    out.append(char)
            elif char == '*':
                ignorable = True
        elif word:  # \foo
            curskip = 0
            if word in destinations:
                ignorable = True
            elif ignorable:
                pass
            elif word in specialchars:
                out.append(specialchars[word])
            elif word == 'uc':
                ucskip = int(arg)
            elif word == 'u':
                c = int(arg)
                if c < 0: c += 0x10000  # NOQA
                if c > 127: out.append(chr(c))  # NOQA
                else: out.append(chr(c))  # NOQA
                curskip = ucskip
        elif hex:  # \'xx
            if curskip > 0:
                curskip -= 1
            elif not ignorable:
                c = int(hex, 16)
                if c > 127: out.append(chr(c))  # NOQA
                else: out.append(chr(c))  # NOQA
        elif tchar:
            if curskip > 0:
                curskip -= 1
            elif not ignorable:
                out.append(tchar)
    return ''.join(out)


def report_file(fname):
    report_filename = 'importer_' + str(datetime.now().strftime('%Y-%m-%d'))
    try:
        with open(report_filename, 'a') as file:
            file.writelines('input')
    except Exception:
        logger.exception('message')


def get_text_from_word(filename):
    doc = docx.Document(filename)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)


def parser(data, fname, is_transcript=False):
    # Original funcion from http://www.kaikaichen.com/?p=539
    articles = []
    dicts = []
    if is_transcript:
        try:
            start = re.search(r'HD', data).start()
            end = re.search(r'Document [a-zA-Z0-9]{25}', data).end()
        except AttributeError:
            logger.warning('Skipping file [%s], HD or Document index not found', fname)
            report_file(fname)
            return []
        a = data[start:end].strip()
        a = '\n' + a
        articles.append(a)
    else:
        try:
            start = re.search(r'\tHD\t', data).start()
        except AttributeError:
            logger.warning('Skipping file [%s], HD index not found', fname)
            report_file(fname)
            return []
        for m in re.finditer(r'Document [a-zA-Z0-9]{25}', data):
            end = m.end()
            a = data[start:end].strip()
            a = '\n\t' + a
            articles.append(a)
            start = end

    # In each article, find all used Intelligence Indexing field codes. Extract
    # content of each used field code, and export as a list of dicts.

    # All field codes (order matters)
    fields = ['CLM', 'SE', 'HD', 'BY', 'CR', 'WC', 'PD', 'ET', 'SN', 'SC', 'ED', 'PG', 'VOL', 'LA', 'CY', 'LP',
              'TD', 'CT', 'RF', 'CO', 'IN', 'NS', 'RE', 'IPC', 'IPD', 'PUB', 'AN']

    for a in articles:
        if is_transcript:
            used = [f for f in fields if re.search(r'\n' + f + r'\s', a)]
            unused = [[i, f] for i, f in enumerate(fields) if not re.search(r'\n' + f + r'\s', a)]
        else:
            used = [f for f in fields if re.search(r'\n\t' + f + r'\t', a)]
            unused = [[i, f] for i, f in enumerate(fields) if not re.search(r'\n\t' + f + r'\t', a)]
        fields_pos = []
        for f in used:
            if is_transcript:
                f_m = re.search(r'\n' + f + r'\s', a)
                f_pos = [f, f_m.start(), f_m.end()]
                fields_pos.append(f_pos)
            else:
                f_m = re.search(r'\t' + f + r'\t', a)
                f_pos = [f, f_m.start(), f_m.end()]
                fields_pos.append(f_pos)
        obs = []
        n = len(used)
        raw_dict = {}
        for i in range(0, n):
            start = fields_pos[i][2]
            if i < n - 1:
                end = fields_pos[i + 1][1]
            else:
                end = len(a)
            content = a[start:end].strip()
            raw_dict[fields_pos[i][0]] = content
            obs.append(content)
        for f in unused:
            obs.insert(f[0], None)
            raw_dict[f[1]] = None
        try:
            raw_dict['id'] = raw_dict['AN'].replace('Document', '').strip()
            raw_dict['text'] = str(raw_dict['LP']) + '\n\n' + str(raw_dict['TD'])
            raw_dict['WC'] = re.findall(r'\d+', raw_dict['WC'].replace(",", ""))[0]
        except AttributeError:
            pass
        try:
            raw_dict['PD'] = datetime.strptime(raw_dict['PD'], '%d %B %Y') if raw_dict['PD'] else None
        except Exception:
            logger.warning('Cannot convert date for %s', raw_dict['AN'][:100])
        try:
            raw_dict['ET'] = datetime.strptime(raw_dict['ET'], '%H:%M') if raw_dict['ET'] else None
        except Exception:
            logger.warning('Cannot convert time for %s', raw_dict['AN'][:100])
        dicts.append(raw_dict)
    return dicts


def process_file(file_location, is_transcript=False):
    filename = os.path.basename(file_location)
    basename = filename.split('.')[-2].strip()
    session = Session()
    if filename.startswith('~$'):
        return None
    logger.info('Procesing file %s...', file_location)
    try:
        if is_transcript:
            file_in_manifest = session.query(FileInfo).filter(FileInfo.file_new_name == basename).first()
            if file_in_manifest is None:
                logger.warning('Filename %s cannot be found in transcripts index', basename)
                return None
            elif file_in_manifest.article_id is not None:
                logger.info('Filename %s already processed with article %s', basename, file_in_manifest.article_id)
                return None
            clean_text = get_text_from_word(file_location)
        else:
            with open(file_location, 'rb') as rtf_file:
                rtf = rtf_file.read().decode()
            clean_text = striprtf(rtf)
    except Exception as e:
        logger.warning('Cannot read from file %s', file_location)
        logger.error('%s %s', type(e), str(e))
        return None
    dicts = parser(clean_text, file_location, is_transcript)
    if len(dicts) == 0:
        logger.error('Cannot extract articles from file %s', file_location)
        return None
    logger.info('Found %d articles in file %s', len(dicts), file_location)
    for dict_item in dicts:
        if is_transcript:
            file_info = session.query(FileInfo).filter_by(
                document_id=dict_item['id'].upper(),
                file_new_name=basename
            ).first()
            if file_info is None:
                logger.warning('Filename %s with article id %s is not found in trancripts list', basename, dict_item['id'])
                continue
        article = session.query(Articles).filter_by(id=dict_item['id']).first()
        if article:
            logger.info('Article %s already exists in database', article.id)
        else:
            try:
                article = Articles(**dict_item)
                session.add(article)
                session.commit()
                if is_transcript:
                    file_info.article_id = dict_item['id']
                    session.commit()
                if 'CO' in dict_item and not is_transcript:
                    match_company(article)
            except Exception:
                logger.exception('message')
    session.close()
    logger.info('Finished parsing file %s...', file_location)


def match_company(article):
    co_list = article.CO.split('|')
    if len(co_list) > 0:
        for organization in co_list:
            inserted = insert_comp_art(organization, article)
    else:
        logger.warning('Could not get company codes for article %s', article.id)


def get_company_by_code(code):
    try:
        session = Session()
        q = session.query(Company).filter(Company.factiva_code == code).first()
        if q is None:
            logger.warning('Could not match company with code %s', code)
            return None
        return q
    except Exception:
        logger.exception('message')
        raise


def insert_comp_art(organization, article):
    try:
        session = Session()
        org_list = organization.split(':')
        code = org_list[0].strip().upper()
        company = get_company_by_code(code)
        if company is None:
            return None
        com_art = CompanyArticle(
            gvkey=company.gvkey,
            article_id=article.id
        )
        if article.NS is not None:
            ns_list = article.NS.split('|')
        else:
            ns_list = []
        i = 0
        for cat in ns_list:
            cat_list = cat.split(':')
            match_cnum = re.match('c\d+', cat_list[0].strip())
            if i > 2 or match_cnum is None:
                continue
            i += 1
            if i == 1:
                com_art.main_category = cat_list[1].strip()
            if i == 2:
                com_art.sub_category = cat_list[1].strip()
        session.add(com_art)
        session.commit()
        logger.info('Matched company %s to article %s', company.factiva_name, com_art.article_id)
        session.close()
    except Exception:
        logger.exception('message')
        raise
