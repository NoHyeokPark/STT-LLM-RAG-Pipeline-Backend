const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

const API_ENDPOINT = 'https://172.31.57.147:8001/whispers/process_video2';
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const FILE_PATH = "C:/ai_project01/uploaded_video/0915.WAV"; // 예: 'C:/Users/YourUser/Videos/test.mp4'

/**
 * 동영상 파일을 지정된 API 엔드포인트로 업로드하는 함수
 * @param {string} url - 요청을 보낼 API URL
 * @param {string} filePath - 업로드할 파일의 로컬 경로
 */
async function uploadVideo(url, filePath) {
    console.log(`업로드를 시작합니다: ${filePath} -> ${url}`);

    // 1. 파일이 존재하는지 확인합니다.
    if (!fs.existsSync(filePath)) {
        console.error(`에러: 파일을 찾을 수 없습니다 - ${filePath}`);
        return;
    }

    // 2. FormData 객체를 생성합니다.
    const form = new FormData();

    // 3. 파일 스트림을 생성하여 form-data에 추가합니다.
    // FastAPI의 'UploadFile' 매개변수 이름('file')과 키를 일치시켜야 합니다.
    const fileName = path.basename(filePath);
    form.append('file', fs.createReadStream(filePath), fileName);
    console.log(`파일을 form-data에 추가했습니다: ${fileName}`);

    try {
        // 4. Axios를 사용하여 POST 요청을 보냅니다.
        const response = await axios.post(url, form, {
            // form-data 라이브러리가 헤더를 자동으로 설정해주므로 중요합니다.
            headers: {
                ...form.getHeaders()
            },
            // 대용량 파일 업로드 시 타임아웃을 방지하기 위해 시간 제한을 늘리거나 0으로 설정
            timeout: 0, 
            // 대용량 파일 업로드 시 메모리 문제를 방지하기 위한 설정
            maxContentLength: Infinity,
            maxBodyLength: Infinity,
        });

        // 5. 서버로부터 받은 응답을 출력합니다.
        console.log('✅ 서버 응답 성공:');
        console.log(JSON.stringify(response.data, null, 2));

    } catch (error) {
        // 6. 에러 처리
        console.error('❌ 업로드 중 에러가 발생했습니다.');
        if (error.response) {
            // 서버가 상태 코드로 응답한 경우
            console.error(`상태 코드: ${error.response.status}`);
            console.error('응답 데이터:', error.response.data);
        } else if (error.request) {
            // 요청은 보냈으나 응답을 받지 못한 경우
            console.error('서버로부터 응답을 받지 못했습니다. 서버가 실행 중인지, URL이 올바른지 확인하세요.');
            console.error(error.request);
        } else {
            // 요청 설정 중 에러가 발생한 경우
            console.error('요청 설정 에러:', error.message);
        }
    }
}

// 스크립트 실행
uploadVideo(API_ENDPOINT, FILE_PATH);