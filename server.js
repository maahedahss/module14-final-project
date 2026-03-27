const http = require('http');
const { randomUUID } = require('crypto');

const PORT = 5000;

let courses = [];

function sendJSON(res, statusCode, data) {
    res.writeHead(statusCode, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end(JSON.stringify(data));
}

function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                resolve(JSON.parse(body));
            } catch (error) {
                reject(error);
            }
        });
        req.on('error', reject);
    });
}

const server = http.createServer(async (req, res) => {
    if (req.method === 'OPTIONS') {
        res.writeHead(200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        });
        res.end();
        return;
    }

    const url = new URL(req.url, `http://localhost:${PORT}`);
    const pathParts = url.pathname.split('/').filter(Boolean);

    if (pathParts[0] === 'api' && pathParts[1] === 'courses') {
        if (req.method === 'GET' && pathParts.length === 2) {
            sendJSON(res, 200, courses);
            return;
        }

        if (req.method === 'POST' && pathParts.length === 2) {
            try {
                const body = await parseBody(req);

                if (!body.name || !body.description || !body.target_date || !body.status) {
                    sendJSON(res, 400, { error: 'Missing required fields' });
                    return;
                }

                const newCourse = {
                    id: randomUUID(),
                    name: body.name,
                    description: body.description,
                    target_date: body.target_date,
                    status: body.status,
                    created_at: new Date().toISOString()
                };

                courses.push(newCourse);
                sendJSON(res, 201, newCourse);
                return;
            } catch (error) {
                sendJSON(res, 400, { error: 'Invalid JSON body' });
                return;
            }
        }

        if (req.method === 'PUT' && pathParts.length === 3) {
            const courseId = pathParts[2];
            const courseIndex = courses.findIndex(c => c.id === courseId);

            if (courseIndex === -1) {
                sendJSON(res, 404, { error: 'Course not found' });
                return;
            }

            try {
                const body = await parseBody(req);
                const updatedCourse = {
                    ...courses[courseIndex],
                    ...body,
                    id: courseId,
                    created_at: courses[courseIndex].created_at
                };

                courses[courseIndex] = updatedCourse;
                sendJSON(res, 200, updatedCourse);
                return;
            } catch (error) {
                sendJSON(res, 400, { error: 'Invalid JSON body' });
                return;
            }
        }

        if (req.method === 'DELETE' && pathParts.length === 3) {
            const courseId = pathParts[2];
            const courseIndex = courses.findIndex(c => c.id === courseId);

            if (courseIndex === -1) {
                sendJSON(res, 404, { error: 'Course not found' });
                return;
            }

            courses.splice(courseIndex, 1);
            sendJSON(res, 200, { message: 'Course deleted successfully' });
            return;
        }
    }

    sendJSON(res, 404, { error: 'Not found' });
});

server.listen(PORT, () => {
    console.log(`🚀 API Server running at http://localhost:${PORT}`);
    console.log(`📚 Endpoints available:`);
    console.log(`   GET    http://localhost:${PORT}/api/courses`);
    console.log(`   POST   http://localhost:${PORT}/api/courses`);
    console.log(`   PUT    http://localhost:${PORT}/api/courses/:id`);
    console.log(`   DELETE http://localhost:${PORT}/api/courses/:id`);
});
