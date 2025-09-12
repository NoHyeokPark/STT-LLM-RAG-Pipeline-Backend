const axios = require('axios');
const fs = require('fs');
const path = require('path');

// FastAPI 서버 주소 (필요시 변경)
const API_ENDPOINT = 'https://172.31.57.147:8001/reports/insert';
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'; // HTTPS 인증서 무시 (개발 환경에서만 사용)

// 1. 커맨드라인에서 입력값 받기
const title = process.argv[2];
const participantsArg = process.argv[3];

// 입력값 유효성 검사
if (!title || !participantsArg) {
    console.error('❌ 사용법: node test.js "문서 제목" "참여자1@메일,참여자2@메일"');
    process.exit(1); // 스크립트 종료
}

// 참여자 목록을 콤마(,)로 구분하여 배열로 변환
const participants = participantsArg.split(',');

// 2. sample.html 파일 읽기
let content;
try {
    const filePath = path.join(__dirname, 'sample.html');
    // 'utf8' 인코딩을 지정하여 파일 내용을 문자열로 읽어옵니다.
    content = fs.readFileSync(filePath, 'utf8');
} catch (err) {
    console.error('❌ Error: sample.html 파일을 읽을 수 없습니다. 파일이 존재하는지 확인하세요.');
    process.exit(1);
}

// 3. API로 보낼 데이터 객체 생성
const dataToSend = {
    title: title,
    participants: participants,
    content: content,
    uploadedAt: "2025-01-01 00:00:00",
};

// 4. API 호출을 위한 비동기 함수 정의
const sendRequest = async () => {
    try {
        console.log('🚀 서버로 데이터를 전송합니다...');
        console.log('-=-=-=-=-=- 전송 데이터 -=-=-=-=-=-');
        console.log(dataToSend);
        console.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=');

        // Axios를 사용하여 POST 요청 보내기
        const response = await axios.post(API_ENDPOINT, dataToSend, {
            headers: {
                'Content-Type': 'application/json',
            },
        });

        console.log('\n✅ 성공! 서버로부터 응답을 받았습니다.');
        console.log('-=-=-=-=-=- 수신 데이터 -=-=-=-=-=-');
        // 서버가 반환한 JSON 데이터를 예쁘게 출력
        console.log(JSON.stringify(response.data, null, 2));
        console.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=');

    } catch (error) {
        console.error('\n❌ 요청 실패!');
        if (error.response) {
            // 서버가 오류 응답을 보낸 경우 (예: 422 유효성 검사 오류)
            console.error(`- 상태 코드: ${error.response.status}`);
            console.error('- 오류 내용:');
            console.error(JSON.stringify(error.response.data, null, 2));
        } else {
            // 네트워크 오류 등 요청 자체가 실패한 경우
            console.error('- 오류 메시지:', error.message);
        }
    }
};

// 5. 함수 실행
sendRequest();