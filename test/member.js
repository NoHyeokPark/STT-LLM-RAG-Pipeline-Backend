// test.js
const fetch = require('node-fetch');
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';  // SSL 검증 끄기
async function fetchStudents() {
    // FastAPI 서버의 주소 (prefix 포함)
    const apiUrl = 'https://172.31.57.147:8001/members/';
    console.log(`요청 보낼 주소: ${apiUrl}`);

    try {
        // API에 GET 요청 보내기
        const response = await fetch(apiUrl);

        // HTTP 응답이 성공적인지 확인
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 응답 본문을 JSON 형태로 파싱
        const students = await response.json();

        // 결과를 콘솔에 출력
        console.log('--- API 응답 성공 ---');
        console.log(students);

    } catch (error) {
        // 에러가 발생하면 콘솔에 에러 메시지 출력
        console.error('--- API 요청 실패 ---');
        console.error(error.message);
    }
}

// 함수 실행
fetchStudents();