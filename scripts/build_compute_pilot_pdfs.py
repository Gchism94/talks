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

def request():
 s=title('DRAFT FOR REVIEW - NOT SUBMITTED','CloudBank ACCESS classroom request')
 s+=[para('Explore ACCESS | Classroom / Training | CloudBank Classroom','Kicker'),para('Supporting request text, not an approved syllabus, CV or completed portal submission. Course, term, PI and numeric resource fields remain to be completed.'),heading('Project and team')]
 for label,key in [('Title','title'),('Institution','institution'),('PI','pi'),('Co-PIs','co_pis'),('Dates','dates'),('Enrollment','students'),('Staff','staff')]:s.append(para(label+': '+R[key],'Small2'))
 s+=[heading('Public overview'),para(R['public_overview']),heading('Teaching objectives'),para('Data science: reproducible cleaning, exploration and small CPU-model validation. MLIS: metadata normalization, collection queries, provenance and portable exports. Use synthetic or rights-cleared public inputs. Required work needs no GPU, paid student account or external managed database.'),heading('Course identifiers to complete'),para(P['courses'][0]['title']+'\n'+P['courses'][1]['title'],'Small2'),PageBreak()]
 s+=title('RESOURCE PLAN - SUBJECT TO PROVIDER CONFIRMATION','Resources and readiness')
 s+=[para('Request 80 persistent student CPU workspaces plus up to six staff identities. Preferred student specification: 2 vCPU, 6 GB RAM and an initial 5 GB home, or a rehearsed provider-approved equivalent. Shared course data: 20 GB/course. Student homes plus shared data total 440 GB before staff homes and provider overhead. Expand only for measured, provider-approved needs. Required GPUs: none.'),para('Active demand: 80 × 8 hours/week × 15 weeks = 9,600 workspace-hours; 2 vCPU each gives 19,200 CPU core-hours. A 25% allowance gives 12,000 workspace-hours / 24,000 core-hours before staff and orchestration/idle use. These are workload descriptions, not CloudBank credit units. Obtain the managed-Classroom request amount from the provider; do not enter Jetstream2 SUs.'),heading('Environment and governance'),para('Request Python/JupyterLab, approved data-analysis and XML/CSV/JSON packages, SQLite, a pinned environment and supported notebook distribution/grading/export. Optional R or MARC tools need confirmation. Appoint course leads, primary/backup operators and TAs before class; this draft does not claim staffing or funds are committed.'),para('A ten-volunteer canary precedes concurrency, isolation, clean assignment runs, save/restart/export, grade receipts, accessibility and independent restore. Keep a small-data CPU fallback. Rosters and grades remain in approved institutional/LMS systems; backup destinations require institutional approval.'),heading('Other resources and term limits'),para('Evaluate campus Puma class groups and CyVerse Pro/TRIF honestly: actual eligibility, quota, queues and class provisioning need confirmation. Clarify the project start/end, export and next-term process with ACCESS/CloudBank; educational extension is not presumed. No supporting research grant is asserted.'),heading('Complete before submission')]
 for item in ['Actual course titles/numbers, instructors, term, enrollments and project dates.','Approved course syllabus PDFs and designated PI/co-PI CV PDFs.','Provider-confirmed limits, accounting/request amount and one-versus-two-project structure.','Named staff, budget/workload commitments, approved data/support and closure plan.']:s.append(para('• '+item,'Small2'))
 s += [link('Provider Classroom request guidance','https://www.cloudbank.org/training/access-cloudbank-classroom'),link('ACCESS request preparation','https://allocations.access-ci.org/prepare-requests'),link('Full reviewed draft, metadata and unsent questions','https://gchism94.github.io/talks/education-compute/access-request.html')]
 doc('cloudbank-access-request.pdf',s)

def brief():
 s=title('TWO-COURSE PILOT | DISCUSSION DRAFT','Reliable computing for teaching')
 s+=[para(P['core_statement'], 'Head'),para(P['decision']),para('Planning baseline: 40 data science students + 40 MLIS students; six preparation weeks, 15 teaching weeks and two export/close weeks. Actual courses, term, instructors, PI, resource limits and operating commitments are pending.'),heading('Decision requested'),para('Approve a preparation/canary ceiling of $6,000 within an illustrative total cash ceiling of $30,000. Release the remaining envelope only after the pre-class checks have dated evidence. Reserve committed faculty/Libraries/finance time separately. This is a proposed staged cap, not an existing authorization.'),heading('One component before a semester')]
 for ph in P['phases']:s.append(para(ph['when']+' - '+ph['title'],'Small2'));s.append(para(ph['body'],'Small2'))
 s+=[PageBreak()]+title('ASSIGNMENTS AND STAFFING','Two CPU workflows; named support')
 for course in P['courses']:
  s += [heading(course['candidate']+' - 40 planned seats'),para(course['assignment']),para('Inputs: '+course['data'],'Small2'),para('Environment: '+course['tools'],'Small2'),para('Acceptance: '+course['acceptance'],'Small2')]
 s+=[heading('Staffing coverage'),para('Primary operator: four hours per teaching week, with 40 preparation and 12 close hours; backup: one hour/week, eight prep and four close. Two TAs: three hours per course/week plus four prep and two close hours each. Each course lead reserves 35 additional pilot hours. Normal course instruction/grading is outside this added-effort estimate.'),para('Publish staffed help windows and a proposed one-business-day first-response target; no 24/7 promise. Escalation: TA/course lead to primary operator, backup/provider and service owner. Primary and backup operators must be different people.'),para('GPU, MESA/CyVerse, NRP and OSPool modules need separate gates. PATh/IDSS eligibility is unconfirmed. Optional resources cannot become required assessment dependencies without their own checks.','Small2'),PageBreak()]
 s+=title('ILLUSTRATIVE USD COSTS - NOT PAY SCALES OR QUOTES','Fund the operations, not only the resource')
 rows=[[para('Role','Cell'),para('Hours','Cell'),para('Loaded rate','Cell'),para('Mode','Cell'),para('Cost','Cell')]]
 for r in B['roles']:rows.append([para(r['role'],'Cell'),str(r['hours']),'$'+str(r['rate']),r['funding'],'$'+f'{r["cost"]:,}'])
 table=Table(rows,colWidths=[195,44,76,66,87],repeatRows=1,hAlign='LEFT');table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6ece7')),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.5,LINE)]));s.append(table)
 s+=[Spacer(1,10)]
 for item in B['nonlabor']:s.append(para(item['item']+': $'+f'{item["amount"]:,}'+' reserve.','Small2'))
 s+=[para('Cash base $24,780 + 20% contingency $4,956 = $29,736. Required in-kind effort $8,220. Cash + committed-time value $37,956.','Head'),para(B['basis'],'Small2'),para(B['cloudbank'],'Small2'),para(B['exclusions'],'Small2'),link('Editable budget and conditional campus-storage comparison','https://gchism94.github.io/talks/education-compute/budget.html'),PageBreak()]
 s+=title('TWELVE CHECKS - ALL PLANNED / NOT RUN','No classroom admission without evidence')
 short=['Named eligible PI, leads, distinct operators and committed funds/coverage.','Approved Classroom route, 80 student + six staff scope, actual limits and term/accounting.','Approved logins; student/instructor isolation and revocation demonstrated.','Both full CPU assignments run cleanly on the pinned environment.','Provider-approved class-load rehearsal; proposed p95 workspace access within five minutes.','Save, stop/restart, export and reopen in the CPU fallback.','Versioned submissions and complete test-grade receipts reconcile in the approved LMS.','Approved data destinations, rights, access roles and retention; no private records on the public site.','Essential keyboard/screen-reader workflows and equivalent assessed CPU/offline route.','Restore on another environment; measured proposed RPO 24 hours/RTO one business day.','Published staffed help/escalation and a rehearsed outage fallback; no 24/7 promise.','Expiry alerts, verified learner/grade exports, closure/deletion and confirmed next-term decision.']
 for i,(g,t) in enumerate(zip(P['checks'],short)):
  s.append(KeepTogether([para(str(i+1)+'. '+g['id'].replace('-',' ').title()+' | '+g['owner'],'Small2'),para(t,'Small2')]))
 s+=[heading('Evidence, evaluation and exit'),para('Keep private account/grade evidence in the institutional register; publish aggregate results only. Measure access and clean-run assignment success, exports/grade receipts, operator-hours, support demand, actual charges and independent-restore timing. Before expiry, provide learner exports, reconcile grades and confirm next-term or closure/retention/deletion arrangements.' ,'Small2'),link('Full readiness register and evidence criteria','https://gchism94.github.io/talks/education-compute/readiness.html'),link('Cohesive program site and source library','https://gchism94.github.io/talks/education-compute/program.html')]
 doc('pilot-brief.pdf',s)

if __name__=='__main__':request();brief();print('Built request and pilot brief PDFs')
