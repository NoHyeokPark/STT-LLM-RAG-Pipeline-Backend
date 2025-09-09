const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

const folderPath = 'C:/ai_project01/uploaded_videos';
const url = 'http://172.31.57.147:8001/whispers/process_videos';
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

async function uploadVideos() {
  try {
    // 폴더에서 비디오 파일들만 필터링
    const files = fs.readdirSync(folderPath)
      .filter(file => {
        const ext = file.toLowerCase();
        return ext.endsWith('.mp4') || ext.endsWith('.webm');
      });

    if (files.length === 0) {
      console.log('업로드할 비디오 파일이 없습니다.');
      return;
    }

    console.log(`${files.length}개의 비디오 파일을 찾았습니다:`, files);

    // FormData 객체 생성
    const formData = new FormData();

    // 각 파일을 FormData에 추가
    files.forEach((filename) => {
      const filePath = path.join(folderPath, filename);
      const fileStream = fs.createReadStream(filePath);
      formData.append('files', fileStream, filename);
    });

    console.log('파일 업로드 시작...');

    // POST 요청 전송
    const response = await axios.post(url, formData, {
      headers: {
        ...formData.getHeaders(),
        'Content-Type': 'multipart/form-data'
      },
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
      timeout: 300000 // 5분 타임아웃
    });

    // 결과 출력
    console.log('=== 응답 결과 ===');
    console.log('Status:', response.data.status);
    console.log('Total Segments:', response.data.total_segments);
    console.log('Processed Files:', response.data.processed_files);
    console.log('Suggested Filename:', response.data.suggested_filename);
    console.log('\n=== 회의록 내용 ===');
    console.log(response.data.transcript);

    // 선택사항: 회의록을 로컬 파일로 저장
    if (response.data.transcript) {
      const outputPath = path.join(__dirname, response.data.suggested_filename);
      fs.writeFileSync(outputPath, response.data.transcript, 'utf8');
      console.log(`\n회의록이 저장되었습니다: ${outputPath}`);
    }

  } catch (error) {
    console.error('업로드 중 오류 발생:');
    if (error.response) {
      console.error('응답 오류:', error.response.data);
      console.error('상태 코드:', error.response.status);
    } else if (error.request) {
      console.error('요청 오류:', error.message);
    } else {
      console.error('기타 오류:', error.message);
    }
  }
}

// 실행
uploadVideos();
