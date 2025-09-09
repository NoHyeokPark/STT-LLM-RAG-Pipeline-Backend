import fetch from 'node-fetch';  // node-fetch import
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const apiUrl = 'https://172.31.57.147:8001/members/';

async function fetchStudents() {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const students = await response.json();
        console.log('--- API 응답 성공 ---');
        console.log(students);
    } catch (err) {
        console.error('--- API 요청 실패 ---');
        console.error(err.message);
    }
}

fetchStudents();