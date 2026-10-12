#!/usr/bin/env python3
"""Create reviewed print companions; requires reportlab (bundled Codex PDF runtime)."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab import rl_config
rl_config.invariant=1
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/'docs/education-compute'
P=json.loads((ROOT/'site/education-compute-pilot.json').read_text());B=P['budget'];R=P['request']
os.environ['SOURCE_DATE_EPOCH']=str(int(datetime.strptime(P['date'],'%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()))
C=colors.HexColor('#222c3a');BLUE=colors.HexColor('#284f8d');TEAL=colors.HexColor('#426f66');LINE=colors.HexColor('#d4d1c5')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Title2',fontName='Helvetica-Bold',fontSize=23,leading=27,textColor=C,spaceAfter=16))
styles.add(ParagraphStyle(name='Head',fontName='Helvetica-Bold',fontSize=14,leading=18,textColor=BLUE,spaceBefore=12,spaceAfter=7))
styles.add(ParagraphStyle(name='Body2',fontName='Helvetica',fontSize=11,leading=14.6,textColor=C,spaceAfter=8))
styles.add(ParagraphStyle(name='Small2',fontName='Helvetica',fontSize=9,leading=12,textColor=C,spaceAfter=6))
styles.add(ParagraphStyle(name='Cell',fontName='Helvetica',fontSize=9,leading=12,textColor=C))
styles.add(ParagraphStyle(name='Kicker',fontName='Helvetica-Bold',fontSize=9,leading=12,textColor=TEAL,spaceAfter=10))
def para(t,s='Body2'):return Paragraph(escape(t).replace('\n','<br/>'),styles[s])
def heading(t):return para(t,'Head')
def title(k,t):return [para(k,'Kicker'),para(t,'Title2')]
def footer(c,d):
 c.saveState();c.setStrokeColor(LINE);c.line(72,47,540,47);c.setFont('Helvetica',8);c.setFillColor(C);c.drawString(72,33,'UArizona Information Science planning proposal | Discussion draft | 12 October 2026');c.drawRightString(540,33,str(d.page));c.restoreState()
def doc(name,story):
 SimpleDocTemplate(str(DEST/name),pagesize=letter,rightMargin=72,leftMargin=72,topMargin=64,bottomMargin=62,title=name.replace('-',' ').replace('.pdf',''),author='Greg Chism',pageCompression=1).build(story,onFirstPage=footer,onLaterPages=footer)
def link(label,url):return Paragraph('<link href="'+url+'" color="#284f8d">'+escape(label)+'</link>',styles['Small2'])

def request(resource, filename, label):
 s=title('DRAFT FOR REVIEW - NOT SUBMITTED',label)
 s+=[para(resource['opportunity'],'Small2'),para(resource['status']),heading('Project and team')]
 for key in ['title','institution','pi','co_pis','dates','students','staff']:s.append(para(key.replace('_',' ').title()+': '+resource[key],'Small2'))
 s+=[heading('Public overview'),para(resource['public_overview']),PageBreak()]
 s+=title('RESOURCE PLAN - UNITS AND AWARD UNCONFIRMED','CPU + GPU scope and other resources')
 s+=[para(resource['resource_justification']),heading('Other available resources'),para(resource['other_resources'],'Small2'),PageBreak()]
 s+=title('COMPLETION AND REVIEW','Before submission and piloting')
 s+=[para(P['decision']),heading('Required completion')]
 for item in resource['attachments']:s.append(para('• '+item,'Small2'))
 s+=[heading('Review and submission steps')]
 for i,item in enumerate(resource['submission_steps']):s.append(para(str(i+1)+'. '+item,'Small2'))
 s+=[para('Supporting draft, not a final tier-specific resource document, syllabus, CV or completed portal submission. All benchmark/readiness checks remain planned.','Small2'),link('ACCESS request preparation','https://allocations.access-ci.org/prepare-requests'),link('Full request and conditional CloudBank branch','https://gchism94.github.io/talks/education-compute/access-request.html')]
 doc(filename,s)

def brief():
 s=title('TWO-COURSE PILOT | DISCUSSION DRAFT','Reliable computing for teaching')
 s+=[para(P['core_statement'], 'Head'),para(P['decision']),para('Planning baseline: 40 data science students + 40 MLIS students; six preparation weeks, 15 teaching weeks and two export/close weeks. Actual courses, term, instructors, PI, resource limits and operating commitments are pending.'),heading('Decision requested'),para('Approve a preparation/canary ceiling of $8,000 within an illustrative total cash ceiling of $35,000. Release the remaining envelope only after the pre-class checks have dated evidence. Reserve committed faculty/Libraries/finance time separately. This is a proposed staged cap, not an existing authorization.'),heading('One component before a semester')]
 for ph in P['phases']:s.append(para(ph['when']+' - '+ph['title'],'Small2'));s.append(para('Exit: '+ph['exit'],'Small2'))
 s+=[PageBreak()]+title('ASSIGNMENTS AND STAFFING','Two CPU workflows; named support')
 for course in P['courses']:
  s += [heading(course['candidate']+' - 40 planned seats'),para(course['assignment']),para('Inputs: '+course['data'],'Small2'),para('Environment: '+course['tools'],'Small2'),para('Acceptance: '+course['acceptance'],'Small2')]
 s+=[heading('Staffing coverage'),para('Primary operator: four hours per teaching week, with 56 preparation and 12 close hours; backup: one hour/week, eight prep and four close. Two TAs: three hours per course/week plus four prep and two close hours each. Each course lead reserves 35 additional pilot hours. Normal course instruction/grading is outside this added-effort estimate.'),para('Publish staffed help windows and a proposed one-business-day first-response target; no 24/7 promise. Escalation: TA/course lead to primary operator, backup/provider and service owner. Primary and backup operators must be different people.'),para('GPU, MESA/CyVerse, NRP and OSPool modules need separate gates. PATh/IDSS eligibility is unconfirmed. Optional resources cannot become required assessment dependencies without their own checks.','Small2'),PageBreak()]
 s+=title('ILLUSTRATIVE USD COSTS - NOT PAY SCALES OR QUOTES','Fund the operations, not only the resource')
 rows=[[para('Role','Cell'),para('Hours','Cell'),para('Loaded rate','Cell'),para('Mode','Cell'),para('Cost','Cell')]]
 for r in B['roles']:rows.append([para(r['role'],'Cell'),str(r['hours']),'$'+str(r['rate']),r['funding'],'$'+f'{r["cost"]:,}'])
 table=Table(rows,colWidths=[195,44,76,66,87],repeatRows=1,hAlign='LEFT');table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6ece7')),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.5,LINE)]));s.append(table)
 s+=[Spacer(1,10)]
 for item in B['nonlabor']:s.append(para(item['item']+': $'+f'{item["amount"]:,}'+' reserve.','Small2'))
 s+=[para('Cash base $27,020 + 20% contingency $5,404 = $32,424. Required in-kind effort $8,220. Cash + committed-time value $40,644.','Head'),para(B['basis'],'Small2'),para(B['cloudbank'],'Small2'),para(B['exclusions'],'Small2'),link('Editable budget and conditional campus-storage comparison','https://gchism94.github.io/talks/education-compute/budget.html'),PageBreak()]
 s+=title('THIRTEEN CHECKS - ALL PLANNED / NOT RUN','Verify before class.')
 short=['Named eligible PI, leads, distinct operators and funded term coverage.','Campus AWS CPU tests and free GPU benchmarks completed; workload manifest, failures and target ACCESS replay recorded.','ACCESS CPU/GPU exchanges, actual quotas/storage, accounting and educational project dates confirmed; CloudBank conditional.','Approved logins, isolation and account revocation demonstrated.','Complete assignments run in the pinned environment; required GPU work fits the verified ACCESS device.','Provider-approved class load rehearsal; proposed p95 workspace access within five minutes.','Save/restart/export demonstrated and outputs reopen elsewhere.','Versioned submissions and test grade receipts reconcile in the approved LMS.','Data rights, access roles, destinations and retention approved.','Essential keyboard/screen-reader workflow and equivalent assessed CPU route demonstrated.','Independent restore measured against proposed 24-hour RPO and one-business-day RTO.','Staffed support, escalation and outage fallback rehearsed; no 24/7 promise.','Expiry warnings, learner/grade exports, closure/deletion and next-term decision documented.']
 for i,(g,t) in enumerate(zip(P['checks'],short)):
  s.append(KeepTogether([para(str(i+1)+'. '+g['id'].replace('-',' ').title()+' | '+g['owner'],'Small2'),para(t,'Small2')]))
 s+=[heading('Evidence, evaluation and exit'),para('Keep private account/grade evidence in the institutional register. Review aggregate access, assignment success, exports, support hours, costs and restore timing. Reconcile grades and complete export, retention and closure before expiry.' ,'Small2'),link('Full readiness register and evidence criteria','https://gchism94.github.io/talks/education-compute/readiness.html')]
 doc('pilot-brief.pdf',s)

if __name__=='__main__':
 request(R,'access-allocation-request.pdf','ACCESS CPU + GPU allocation request')
 request(P['cloudbank_request'],'cloudbank-access-request.pdf','Conditional CloudBank ACCESS concept')
 brief()
 print('Built ACCESS request, conditional CloudBank concept and pilot brief PDFs')
