영상 제작 실무 교본 — 재디자인 소스 v9.6

v9.6 변경 (인쇄소 요청: 전체 쪽수는 8의 배수)
- 책 끝 NOTE 페이지를 4쪽 늘려 516쪽 → 520쪽 (= 8 × 65). 표지(p1 앞표지, p520 뒤표지)를 포함한 PDF 전체 쪽수 기준입니다.
- 본문·도판·목차 쪽번호·장도비라 위치는 v9.5와 같습니다 (장도비라는 모두 홀수 쪽).
- build2.py 의 끝 채움 규칙을 4의 배수에서 8의 배수로 바꿨습니다 (SIG=8: NOTE 페이지로 채운 뒤 표3 백면, 뒤표지).

book/        조판 소스 (HTML parts, CSS, 빌드 스크립트)
book/img     원고 원본 도판 (최적화본)
book/img_new 재디자인에서 새로 만든 사진·일러스트·도판
tools/       보조 스크립트 (흰 배경 처리, 측정값 보호 meas.py, SVG 라벨 맞춤 fitsvg.js, 최종 PDF 정리 finalize_pdf.py)
(src/ 원고 원본 PDF·추출 텍스트·작업용 목록은 공개본에 넣지 않았습니다. 책을 빌드하는 데는 필요하지 않습니다.)

빌드: book/ 폴더에서 BOOK_Z=1 python3 build2.py  (Playwright·Chromium·pdftotext·pypdf 필요)
최종 PDF: 위 폴더에서  ACCEPT_DIFF=16,17 python3 ../tools/finalize_pdf.py . <출력.pdf> "영상 제작 실무 교본 — 재디자인판" "안지아"
  (쪽 위치 확인용 보이지 않는 표식을 지운 뒤 다시 렌더링합니다. 16–17쪽 FAQ 마지막 한 줄 위치 차이는 v9.5에서 검토·허용한 것과 같습니다.)
build2.py 와 render.js 안의 meas.py / fitsvg.js 경로는 작업 환경의 절대 경로이므로
다른 컴퓨터에서는 tools/ 경로로 바꿔 주십시오.
