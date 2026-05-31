function getFormData(form) {
    const raw = new FormData(form);
    const data = {};
    for (const [key, value] of raw.entries()) {
        if (data[key] !== undefined) {
            if (!Array.isArray(data[key])) {
                data[key] = [data[key]];
            }
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }
    return data;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function nl2br(text) {
    return escapeHtml(text).replaceAll("\n", "<br>");
}

function showMessage(container, html) {
    container.classList.remove("d-none");
    container.innerHTML = html;
}

function renderProfileCard(profile) {
    const dimensions = Object.entries(profile.dimensions || {})
        .map(([key, value]) => {
            const weight = profile.weights?.[key] ?? 0;
            return `
                <div class="profile-card">
                    <div class="d-flex justify-content-between align-items-start gap-3">
                        <div>
                            <h3 class="h6 mb-2">${escapeHtml(key)}</h3>
                            <p class="text-secondary mb-0">${escapeHtml(value)}</p>
                        </div>
                        <span class="pill">权重 ${Number(weight).toFixed(2)}</span>
                    </div>
                </div>
            `;
        })
        .join("");

    const suggestions = (profile.refresh_suggestions || [])
        .map((item) => {
            const priority = item.priority || "low";
            return `
                <div class="mini-card">
                    <strong class="priority-${priority}">${escapeHtml(item.dimension)}</strong>
                    <span>${escapeHtml(item.message)}</span>
                    <small>优先级：${escapeHtml(priority)}</small>
                </div>
            `;
        })
        .join("");

    return `
        <div class="col-12">
            <div class="result-panel">
                <div class="d-flex flex-wrap gap-3 justify-content-between">
                    <div>
                        <p class="mb-1 text-secondary">综合记忆强度</p>
                        <h3 class="mb-0">${Number(profile.memory_strength || 0).toFixed(2)}</h3>
                    </div>
                    <div>
                        <p class="mb-1 text-secondary">最近主题</p>
                        <h3 class="mb-0">${escapeHtml(profile.last_study_topic || "未设置")}</h3>
                    </div>
                </div>
            </div>
        </div>
        ${dimensions}
        <div class="col-12">
            <div class="glass-panel">
                <h3 class="h5 mb-3">复习建议</h3>
                <div class="stack-list">${suggestions}</div>
            </div>
        </div>
    `;
}

function renderResourceItem(item) {
    return `
        <div class="mini-card">
            <div class="d-flex flex-wrap gap-2 justify-content-between align-items-start">
                <div>
                    <strong>${escapeHtml(item.title)}</strong>
                    <span>${escapeHtml(item.description)}</span>
                    <small>${escapeHtml(item.topic)} · ${escapeHtml(item.resource_type)}</small>
                </div>
                <span class="pill">${escapeHtml(item.resource_type)}</span>
            </div>
            <div class="markdown-block mt-3">${nl2br(item.content)}</div>
            <small class="text-secondary mt-2">文件：${escapeHtml(item.file_path || "")}</small>
        </div>
    `;
}

function renderStudyPath(item) {
    const nodes = (item.path_nodes || [])
        .map((node) => `
            <div class="timeline-card">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <strong>Day ${escapeHtml(node.day)}</strong>
                    <span class="pill">${escapeHtml(node.stage)}</span>
                </div>
                <p class="mb-1">${escapeHtml(node.task)}</p>
                <small class="text-secondary">${escapeHtml(node.date)} · ${escapeHtml(node.review_tip)}</small>
            </div>
        `)
        .join("");

    const actions = (item.recommendations || [])
        .map((action) => `<li>${escapeHtml(action)}</li>`)
        .join("");

    return `
        <div class="mini-card">
            <div class="d-flex flex-wrap gap-2 justify-content-between align-items-start mb-3">
                <div>
                    <strong>${escapeHtml(item.topic)}</strong>
                    <span>${escapeHtml(item.target_days)} 天路径 · 当前进度 ${Number(item.progress || 0).toFixed(0)}%</span>
                </div>
                <span class="pill">${escapeHtml(item.status)}</span>
            </div>
            <div class="stack-list mb-3">${nodes}</div>
            <div>
                <strong>路径建议</strong>
                <ul class="mt-2 mb-0">${actions}</ul>
            </div>
        </div>
    `;
}

function renderAnswerItem(item) {
    return `
        <div class="mini-card">
            <strong>${escapeHtml(item.topic || "未指定主题")}</strong>
            <span>Q: ${escapeHtml(item.question)}</span>
            <div class="markdown-block mt-2">${nl2br(item.answer)}</div>
            <small class="text-secondary">置信度 ${Number(item.confidence || 0).toFixed(2)} · ${escapeHtml(item.created_at)}</small>
        </div>
    `;
}

function renderReportItem(item) {
    const scores = Object.entries(item.dimension_scores || {})
        .map(([key, value]) => `<li>${escapeHtml(key)}：${Number(value).toFixed(2)}</li>`)
        .join("");
    const actions = (item.optimization_actions || [])
        .map((action) => `<li>${escapeHtml(action)}</li>`)
        .join("");

    return `
        <div class="mini-card">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <strong>${escapeHtml(item.title)}</strong>
                <span class="pill">总分 ${Number(item.overall_score).toFixed(2)}</span>
            </div>
            <span>${escapeHtml(item.report_period)}</span>
            <p class="mt-3 mb-2">${escapeHtml(item.summary)}</p>
            <strong>维度评分</strong>
            <ul class="mt-2">${scores}</ul>
            <strong>优化动作</strong>
            <ul class="mt-2 mb-0">${actions}</ul>
        </div>
    `;
}

async function refreshUsers() {
    const response = await axios.get("/api/users");
    return response.data.data || [];
}

function appendToast(message, type = "success") {
    const existing = document.getElementById("globalToast");
    if (existing) existing.remove();
    const toast = document.createElement("div");
    toast.id = "globalToast";
    toast.className = "position-fixed top-0 end-0 p-3";
    toast.style.zIndex = "1080";
    toast.innerHTML = `
        <div class="toast show text-bg-${type === "success" ? "success" : "danger"} border-0">
            <div class="d-flex">
                <div class="toast-body">${escapeHtml(message)}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    document.body.appendChild(toast);
}

function getSelectedUserId(selector) {
    const element = document.querySelector(selector);
    return element ? element.value : "";
}

document.addEventListener("DOMContentLoaded", () => {
    const page = window.pageConfig?.page;

    if (page === "index") {
        const userForm = document.getElementById("userForm");
        const orchestrateForm = document.getElementById("orchestrateForm");
        const resultBox = document.getElementById("orchestrateResult");

        userForm?.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const payload = getFormData(userForm);
                await axios.post("/api/users", payload);
                appendToast("用户创建成功");
                window.location.reload();
            } catch (error) {
                appendToast(error.response?.data?.message || "保存失败", "danger");
            }
        });

        orchestrateForm?.addEventListener("submit", async (event) => {
            event.preventDefault();
            showMessage(resultBox, "正在调度多个智能体，请稍候...");
            try {
                const payload = getFormData(orchestrateForm);
                payload.user_id = Number(payload.user_id);
                const response = await axios.post("/api/agents/orchestrate", payload);
                const data = response.data.data;
                showMessage(
                    resultBox,
                    `
                    <h3 class="h5 mb-3">协同完成</h3>
                    <p class="text-secondary">参与智能体：${data.agents.map(escapeHtml).join(" / ")}</p>
                    <div class="stack-list">
                        <div class="mini-card">
                            <strong>学习画像</strong>
                            <span>综合记忆强度：${Number(data.profile.memory_strength).toFixed(2)}</span>
                        </div>
                        <div class="mini-card">
                            <strong>资源数量</strong>
                            <span>${data.resources.length} 个</span>
                        </div>
                        <div class="mini-card">
                            <strong>学习路径</strong>
                            <span>${escapeHtml(data.study_path.topic)} · ${escapeHtml(data.study_path.target_days)} 天</span>
                        </div>
                        <div class="mini-card">
                            <strong>评估总分</strong>
                            <span>${Number(data.report.overall_score).toFixed(2)}</span>
                        </div>
                    </div>
                    `
                );
            } catch (error) {
                showMessage(resultBox, error.response?.data?.message || "协同流程失败");
            }
        });
    }

    if (page === "profile") {
        const form = document.getElementById("profileForm");
        const button = document.getElementById("loadProfileBtn");
        const result = document.getElementById("profileResult");

        form?.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const payload = getFormData(form);
                payload.user_id = Number(payload.user_id);
                const response = await axios.post("/api/profile/build", payload);
                result.innerHTML = renderProfileCard(response.data.data);
                appendToast("画像已更新");
            } catch (error) {
                appendToast(error.response?.data?.message || "画像生成失败", "danger");
            }
        });

        button?.addEventListener("click", async () => {
            const userId = getSelectedUserId('#profileForm select[name="user_id"]');
            if (!userId) {
                appendToast("请先选择用户", "danger");
                return;
            }
            const response = await axios.get(`/api/profile/${userId}`);
            result.innerHTML = renderProfileCard(response.data.data);
        });
    }

    if (page === "resource") {
        const form = document.getElementById("resourceForm");
        const loadBtn = document.getElementById("loadResourcesBtn");
        const result = document.getElementById("resourceResult");

        async function loadResources() {
            const userId = getSelectedUserId('#resourceForm select[name="user_id"]');
            const url = userId ? `/api/resources?user_id=${userId}` : "/api/resources";
            const response = await axios.get(url);
            result.innerHTML = (response.data.data || []).map(renderResourceItem).join("") || '<div class="empty-state">暂无资源记录</div>';
        }

        form?.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const payload = getFormData(form);
                payload.user_id = Number(payload.user_id);
                payload.resource_types = Array.isArray(payload.resource_types)
                    ? payload.resource_types
                    : [payload.resource_types];
                await axios.post("/api/resources/generate", payload);
                appendToast("资源已生成");
                await loadResources();
            } catch (error) {
                appendToast(error.response?.data?.message || "资源生成失败", "danger");
            }
        });

        loadBtn?.addEventListener("click", loadResources);
        loadResources();
    }

    if (page === "study") {
        const form = document.getElementById("studyForm");
        const loadBtn = document.getElementById("loadStudyBtn");
        const result = document.getElementById("studyResult");

        async function loadStudy() {
            const userId = getSelectedUserId('#studyForm select[name="user_id"]');
            const url = userId ? `/api/study-paths?user_id=${userId}` : "/api/study-paths";
            const response = await axios.get(url);
            result.innerHTML = (response.data.data || []).map(renderStudyPath).join("") || '<div class="empty-state">暂无学习路径</div>';
        }

        form?.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const payload = getFormData(form);
                payload.user_id = Number(payload.user_id);
                payload.target_days = Number(payload.target_days);
                await axios.post("/api/study-paths/generate", payload);
                appendToast("学习路径已生成");
                await loadStudy();
            } catch (error) {
                appendToast(error.response?.data?.message || "路径生成失败", "danger");
            }
        });

        loadBtn?.addEventListener("click", loadStudy);
        loadStudy();
    }

    if (page === "answer") {
        const form = document.getElementById("answerForm");
        const streamBtn = document.getElementById("streamAnswerBtn");
        const currentBox = document.getElementById("answerCurrent");
        const historyBox = document.getElementById("answerHistory");
        const loadBtn = document.getElementById("loadAnswersBtn");

        async function loadAnswers() {
            const userId = getSelectedUserId('#answerForm select[name="user_id"]');
            const url = userId ? `/api/answers?user_id=${userId}` : "/api/answers";
            const response = await axios.get(url);
            historyBox.innerHTML = (response.data.data || []).map(renderAnswerItem).join("") || '<div class="empty-state">暂无答疑记录</div>';
        }

        form?.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const payload = getFormData(form);
                payload.user_id = Number(payload.user_id);
                const response = await axios.post("/api/answers", payload);
                currentBox.innerHTML = renderAnswerItem(response.data.data);
                appendToast("答疑完成");
                await loadAnswers();
            } catch (error) {
                appendToast(error.response?.data?.message || "答疑失败", "danger");
            }
        });

        streamBtn?.addEventListener("click", async () => {
            const payload = getFormData(form);
            if (!payload.user_id || !payload.question) {
                appendToast("请先选择用户并输入问题", "danger");
                return;
            }
            currentBox.innerHTML = '<div class="mini-card">正在流式生成回答...</div>';
            const query = new URLSearchParams({
                user_id: payload.user_id,
                question: payload.question,
                topic: payload.topic || "",
            });
            const source = new EventSource(`/api/answers/stream?${query.toString()}`);
            let content = "";

            source.addEventListener("chunk", (event) => {
                const data = JSON.parse(event.data);
                content += data.content || "";
                currentBox.innerHTML = `
                    <div class="mini-card">
                        <strong>流式回答中</strong>
                        <div class="markdown-block mt-2">${nl2br(content)}</div>
                    </div>
                `;
            });

            source.addEventListener("done", async (event) => {
                const data = JSON.parse(event.data);
                currentBox.innerHTML = renderAnswerItem(data);
                source.close();
                appendToast("流式回答完成");
                await loadAnswers();
            });
        });

        loadBtn?.addEventListener("click", loadAnswers);
        loadAnswers();
    }

    if (page === "evaluate") {
        const form = document.getElementById("evaluateForm");
        const result = document.getElementById("evaluateResult");
        const loadBtn = document.getElementById("loadReportsBtn");

        async function loadReports() {
            const userId = getSelectedUserId('#evaluateForm select[name="user_id"]');
            const url = userId ? `/api/evaluations?user_id=${userId}` : "/api/evaluations";
            const response = await axios.get(url);
            result.innerHTML = (response.data.data || []).map(renderReportItem).join("") || '<div class="empty-state">暂无评估报告</div>';
        }

        form?.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const payload = getFormData(form);
                payload.user_id = Number(payload.user_id);
                await axios.post("/api/evaluations/generate", payload);
                appendToast("评估报告已生成");
                await loadReports();
            } catch (error) {
                appendToast(error.response?.data?.message || "评估生成失败", "danger");
            }
        });

        loadBtn?.addEventListener("click", loadReports);
        loadReports();
    }
});

