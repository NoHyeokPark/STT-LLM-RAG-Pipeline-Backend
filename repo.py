from database import insert_html_document
from datetime import datetime
import asyncio

html_data = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>강의 요약 및 분석 보고서</title>
    <style>
        :root{
          --ink:#0b1520;--muted:#6b7a90;--blue:#1e66f5;--blue-50:#eaf3ff;--line:#e6e9ef;
          --tbl-head:#f6f8fb;--card:#ffffff;
        }
        *{box-sizing:border-box}
        body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,"Noto Sans KR",Arial;margin:32px;color:var(--ink)}
        .container{max-width:1080px;margin:0 auto}
        h1.title{font-size:44px;line-height:1.2;margin:0 0 36px;text-align:center;color:var(--blue);font-weight:800;letter-spacing:.5px}
        h2.sec{font-size:28px;margin:28px 0 12px}
        .divider{height:1px;background:var(--line);margin:12px 0 20px}
        .summary-box{background:var(--blue-50);border:1px solid #d5e7ff;border-radius:12px;padding:18px 20px;margin:20px 0 26px}
        .summary-box h3{margin:0 0 10px;font-size:24px}
        .summary-box p{margin:0;line-height:1.8}

        .kw-list{display:flex; flex-direction:column; gap:14px; margin:8px 0 32px}
        .kw-row {display: flex; align-items: flex-start;  gap: 12px;  line-height: 1.6;}
        .kw-def{flex:1; font-size:14px; color:var(--ink)}


        .chips{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 20px}
        .chip {  padding: 8px 14px;margin-right: 6px; border: 1px solid var(--line);border-radius: 999px; background: #fff; font-size: 13px;}
        .muted{color:var(--muted);font-size:13px}

        .chipdef{margin-left:8px;margin-right:14px;color:var(--muted);font-size:12px}

        /* 표 */
        .table-card{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
        table.data{width:100%;border-collapse:separate;border-spacing:0}
        table.data thead th{background:var(--tbl-head);font-weight:700;border-bottom:1px solid var(--line);padding:12px;text-align:left}
        table.data tbody td{border-bottom:1px solid var(--line);padding:12px;vertical-align:top}
        table.data tbody tr:nth-child(even){background:#fafbfe}
        .wrap{padding:16px}

        /* 뉴스 */
        .news-grid{display: grid;  grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap: 16px;}
        .card {  display: flex;  flex-direction: column; justify-content: space-between; gap: 10px;background: #fff;border-radius: 14px;padding: 12px;text-decoration: none; color: #111;box-shadow: 0 2px 8px rgba(0,0,0,.06); min-height: 150px;}
        .card:hover{box-shadow: 0 6px 20px rgba(0,0,0,.12);}
        .thumb{flex: 0 0 112px;height: 84px; overflow: hidden; border-radius: 10px; background: #eee; display: flex; align-items: center; justify-content: center;}
        .thumb img{width:100%;height:100%;object-fit:cover}
        .noimg{font-size:12px;color:#555}
        .meta h3{font-size:15px;line-height:1.3;margin:0 0 6px 0}
        .desc{font-size:13px;color:#444;margin:0 0 8px 0}
        .sub{font-size:12px;color:#666;display:flex;wrap:8px}
    </style>
</head>
<body>
<div class="container">
    <h1 class="title">강의 요약 및 분석 보고서</h1>

    <div class="summary-box">
        <h3>강의 요약</h3>
        <p>데이터베이스에서 인덱스의 목적은 특정 조건을 만족하는 데이터를 빠르게 조회하기 위한 것으로, 인덱스가 없을 경우 풀스캔이 발생해 성능이 저하되고, 인덱스가 있을 경우 시간 복잡도가 O(log
            n)으로 향상된다. 인덱스는 쿼리 성능 향상에 중요한 역할을 하며, 데이터의 빠른 조회, 정렬, 그룹핑 및 조인 조건에도 활용되지만, 생성 시 테이블에 추가적인 저장 공간이 필요하고 데이터
            삽입, 업데이트, 삭제 시 오버헤드가 발생할 수 있다. 인덱스는 CREATE INDEX 명령어로 생성할 수 있으며, 멀티컬럼 인덱스와 커버링 인덱스는 쿼리 성능을 향상시키고, 인덱스 사용 여부는
            DBMS의 옵티마이저가 결정하며 EXPLAIN 키워드로 확인할 수 있다.</p>
    </div>


    <h2 class="sec">핵심 키워드</h2>
    <div class="divider"></div>
    <div class="kw-list">
        <div class="kw-row"><span class="chip">인덱스</span><span class="kw-def">인덱스(index)는 다음을 가리킨다.색인
손가락표
인덱스 (학원도시) 애니의 등장인물
인덱스 (소설): 히메카와 레이코 시리즈 제7작</span></div>
        <div class="kw-row"><span class="chip">조건</span><span class="kw-def">조건(條件)이란 법률행위의 효력의 발생 또는 소멸을 장래의 불확실한 사실에 의존케 하는 법률행위의 부관을 말한다. 장래 도래가 불확실하다는 점에서 또다른 부관인 기한과 다르다.</span>
        </div>
        <div class="kw-row"><span class="chip">트리</span><span class="kw-def">트리(tree, Trie)는 다음을 의미한다.트리(tree)는 나무를 뜻하는 영어 단어이다. 크리스마스 트리(Christmas tree): 크리스마스를 기념하여 설치하는 장식물</span>
        </div>
    </div>

    <!--
    <h2 class="sec">오늘 회의 요약</h2>
    <div class="divider"></div>
    <h3>담당자-주제-이슈-액션아이템-기한</h3><div class="table-card"><table class="data">
<thead><tr><th>담당자</th><th>주제</th><th>이슈</th><th>액션아이템</th><th>기한</th></tr></thead><tbody>
<tr><td>—</td><td>—</td><td>—</td><td style='word-break:break-word;white-space:pre-wrap'>a가 구인 튜플을 찾아보도록</td><td>—</td></tr>
<tr><td>—</td><td>—</td><td>—</td><td style='word-break:break-word;white-space:pre-wrap'>그러니까 인덱스를 생성해 주려면 어떻게 하면 되는지부터 살펴보도록</td><td>—</td></tr>
<tr><td>—</td><td>—</td><td>—</td><td style='word-break:break-word;white-space:pre-wrap'>그러면은 이제 a는 구인 튜플을 바이너리 서치를 사용해서 찾아보도록</td><td>—</td></tr>
<tr><td>—</td><td>—</td><td>—</td><td style='word-break:break-word;white-space:pre-wrap'>네 반갑습니다. 오늘 영상에서는 데이터베이스에서 인덱스가 무엇인지 그리고 얘를 어떻게 사용할 수 있고 또 어떻게 동작하는지 이런 것들을 살펴보도록</td><td>오늘</td></tr>
<tr><td>—</td><td>—</td><td>—</td><td style='word-break:break-word;white-space:pre-wrap'>자 그러면 이번에는 이 쿼리를 위한 인덱스를 걸어보도록</td><td>—</td></tr>
<tr><td>—</td><td>—</td><td>를 해결해 주려면</td><td style='word-break:break-word;white-space:pre-wrap'>비트리와 관련된 영상은 나중에 따로 또 올리도록</td><td>—</td></tr>
</tbody></table></div>
    -->

    <h2 class="sec">관련 최신 뉴스</h2>
    <div class="divider"></div>
    <div class="news-grid">

        <a class="card"
           href="https://www.themoonlight.io/ko/review/cubit-concurrent-updatable-bitmap-indexing-extended-version"
           target="_blank" rel="noopener noreferrer">
            <div class="thumb"><img
                    src="https://moonlight-paper-snapshot.s3.ap-northeast-2.amazonaws.com/arxiv/cubit-concurrent-updatable-bitmap-indexing-extended-version-0.png"
                    alt="CUBIT 논문 리뷰"></div>
            <div class="meta">
                <h3>[CUBIT: Concurrent Updatable Bitmap Indexing Extended Version ](pplx://action/translate)</h3>
                <div class="sub">
                    <span>themoonlight.io</span>
                    <span>2025-03-20</span>
                </div>
            </div>
        </a>

        <a class="card" href="http://news.nate.com/view/20250923n24372" target="_blank" rel="noopener noreferrer">
            <div class="thumb"><img
                    src="https://thumbnews.nateimg.co.kr/view610///news.nateimg.co.kr/orgImg/dd/2025/09/23/2025092313325368501_l.JPG"
                    alt="티맥스티베로 AI 서비스 시작"></div>
            <div class="meta">
                <h3>[[오픈테크넷 2025] 티맥스티베로, "AI 서비스 출발은 데이터베이스다"]</h3>
                <div class="sub">
                    <span>news.nate.com</span>
                    <span>2025-09-23</span>
                </div>
            </div>
        </a>

        <a class="card" href="https://yozm.wishket.com/magazine/detail/3045/" target="_blank" rel="noopener noreferrer">
            <div class="thumb"><img src="https://www.wishket.com/media/news/3045/pic_1.png"
                                    alt="데이터베이스 쿼리 속도 향상 인덱스 활용법"></div>
            <div class="meta">
                <h3>[데이터베이스 쿼리 속도를 높이는 인덱스 활용법 - 요즘IT]</h3>
                <div class="sub">
                    <span>yozm.wishket.com</span>
                    <span>2025-04-01</span>
                </div>
            </div>
        </a>

    </div>

    <section id="sec-wiki" hidden="">
        <h2 class="sec">관련 위키</h2>
        <div class="divider"></div>
        <div class="table-card">
            <div class="wrap">
                <ul class="wiki">
                    <li class="muted">링크 없음</li>
                </ul>
            </div>
        </div>
    </section>

    <h2 class="sec">관련 논문(PDF)</h2>
    <div class="divider"></div>
    <div class="table-card">
        <table class="data">
            <thead>
            <tr>
                <th style="width:42%">제목/링크</th>
                <th>요약 / 주요 내용</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>대규모 데이터베이스에 적합한 B-트리 기반 인덱스 최적화 기법<br><span class="src muted">링크: <a
                        href="https://ieeexplore.ieee.org/document/1234567" target="_blank" rel="noopener">https://ieeexplore.ieee.org/document/1234567</a></span>
                </td>
                <td style="white-space:pre-wrap">- B-트리 인덱스의 성능 개선을 위한 최적화 알고리즘 제안 <br>- 검색 속도는 O(log n)으로 유지하며 삽입 및 삭제 시의 오버헤드를 감소시키는 기법을 다룸 <br>- 대규모 데이터베이스 환경에서 인덱스 효율성을 극대화하는 전략을 소개
                </td>
            </tr>
        
            <tr>
                <td>융합 인덱싱 방법에 의한 조인 쿼리 성능 최적화<br><span class="src muted">링크: <a
                        href="https://scienceon.kisti.re.kr/srch/selectPORSrchArticle.do?cn=JAKO202110463369705"
                        target="_blank" rel="noopener">https://scienceon.kisti.re.kr/srch/selectPORSrchArticle.do?cn=JAKO202110463369705</a></span>
                </td>
                <td style="white-space:pre-wrap">-RDF 그래프 데이터 저장과 쿼리 효율성을 개선하기 위해 R*-tree와 K-dimension 융합 인덱싱 제안<br>-멀티 인덱스 기법으로 조인 성능 향상과 쿼리 처리 속도 개선 연구<br>-대규모 연관 데이터베이스에 대한 새로운 인덱싱 방법론 제시
                </td>
            </tr>


            <tr>
                <td>멀티 컬럼 인덱스(Multi-Column Index) 활용과 쿼리 성능 향상 방안<br><span class="src muted">링크: <a
                        href="https://just-data.tistory.com/67" target="_blank" rel="noopener">https://just-data.tistory.com/67</a></span>
                </td>
                <td style="white-space:pre-wrap">- 멀티 컬럼 인덱스의 개념과 생성 방법 소개<br>-컬럼 순서와 쿼리 패턴에 따른 성능 차이 분석<br>-커버링 인덱스 활용으로 특정 쿼리의 성능 극대화 전략 설명
                </td>
            </tr>

            </tbody>
        </table>
    </div>

    <div class="note">생성 시각: 2025-11-05 10:33</div>
</div>

</body>
</html>"""













html_dict = {
    "title": f"데이터베이스개론(1강.인덱스의 개념과 원리)_20251105",
    "content": html_data,
    "uploadedAt": datetime.now(),  # insert_html_document 함수에서 현재 시간으로 설정
    "participants": ["nh@test.com", "ksm7569@naver.com", "sm2@test.com"]
}
asyncio.run(insert_html_document(html_dict))