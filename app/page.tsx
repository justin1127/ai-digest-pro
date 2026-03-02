export default function DigestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-800">AGI 决策情报</h1>
              <p className="text-sm text-slate-500 mt-1">2026.03.02 | 星期日</p>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full">已更新</span>
              <button className="text-sm bg-slate-800 text-white px-4 py-2 rounded-lg hover:bg-slate-700 transition">
                分享
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-200">
            <p className="text-xs text-slate-500">洞察</p>
            <p className="text-2xl font-bold text-slate-800">4</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-200">
            <p className="text-xs text-slate-500">新闻</p>
            <p className="text-2xl font-bold text-slate-800">8</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-200">
            <p className="text-xs text-slate-500">来源</p>
            <p className="text-2xl font-bold text-slate-800">14</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-200">
            <p className="text-xs text-slate-500">阅读时间</p>
            <p className="text-2xl font-bold text-slate-800">5min</p>
          </div>
        </div>

        {/* Meta Insights */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">🧠</span>
            <h2 className="text-xl font-bold text-slate-800">元洞察 · Meta Insights</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex gap-4 p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-xl border border-red-100">
              <span className="text-lg font-bold text-red-600 shrink-0">01</span>
              <div>
                <p className="text-slate-800 font-medium leading-relaxed">
                  <span className="text-red-600 font-semibold">AI军事化成为国家战略核心</span>，伦理与政策冲突白热化。Anthropic因坚持"不用于致命自主武器"红线遭五角大楼威胁封杀。
                </p>
              </div>
            </div>
            
            <div className="flex gap-4 p-4 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl border border-amber-100">
              <span className="text-lg font-bold text-amber-600 shrink-0">02</span>
              <div>
                <p className="text-slate-800 font-medium leading-relaxed">
                  <span className="text-amber-600 font-semibold">大模型融资进入"主权级"规模</span>。OpenAI寻求$110B巨额融资并与Amazon深度绑定，AI基础设施化趋势加速。
                </p>
              </div>
            </div>
            
            <div className="flex gap-4 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border border-blue-100">
              <span className="text-lg font-bold text-blue-600 shrink-0">03</span>
              <div>
                <p className="text-slate-800 font-medium leading-relaxed">
                  <span className="text-blue-600 font-semibold">AI Agent从"对话工具"进化为"自主代理"</span>。三星S26 Gemini深度整合，标志着手机从"触控交互"转向"意图预测+代理执行"。
                </p>
              </div>
            </div>
            
            <div className="flex gap-4 p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border border-emerald-100">
              <span className="text-lg font-bold text-emerald-600 shrink-0">04</span>
              <div>
                <p className="text-slate-800 font-medium leading-relaxed">
                  <span className="text-emerald-600 font-semibold">中国AI从"参数竞赛"转向"Agent应用落地"</span>。春节档Qwen3.5/GLM-5/Seedance集中发布，201语言+全球化布局。
                </p>
              </div>
            </div>
          </div>

          {/* Questions */}
          <div className="mt-6 p-4 bg-slate-50 rounded-xl">
            <p className="text-sm font-semibold text-slate-600 mb-3">❓ 深度思考</p>
            <ul className="space-y-2 text-sm text-slate-700">
              <li>• 当手机全面进化为具身代理的"遥控器"，传统App的入口地位是否会彻底坍塌？</li>
              <li>• 如果OpenAI独占2GW算力，中小型AI公司如何在巨头构建的算力围墙中寻找溢价空间？</li>
              <li>• AI公司的"不作恶"承诺在军方合同面前是否只是营销口号？</li>
            </ul>
          </div>
        </section>

        {/* Strategic Anchor */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">⚓</span>
            <h2 className="text-xl font-bold text-slate-800">战略锚点 · Strategic Anchors</h2>
          </div>
          
          <div className="border-l-4 border-blue-500 pl-6 py-2">
            <h3 className="text-lg font-bold text-slate-800 mb-4">
              Anthropic vs 五角大楼：AI伦理与军事需求的终极对决
            </h3>
            
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="p-3 bg-red-50 rounded-lg">
                <p className="text-xs font-semibold text-red-600 mb-1">WHAT</p>
                <p className="text-sm text-slate-700">特朗普政府宣布禁止联邦使用Claude，但五角大楼仍用其策划伊朗空袭</p>
              </div>
              <div className="p-3 bg-amber-50 rounded-lg">
                <p className="text-xs font-semibold text-amber-600 mb-1">HOW</p>
                <p className="text-sm text-slate-700">五角大楼要求"任何合法用途"，Anthropic坚持两条红线拒绝妥协</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-xs font-semibold text-blue-600 mb-1">WHY</p>
                <p className="text-sm text-slate-700">AI行业首次因伦理立场遭政府封杀，Claude是唯一IL-6安全许可模型</p>
              </div>
            </div>
            
            <div className="p-4 bg-slate-50 rounded-xl">
              <p className="text-sm font-semibold text-slate-600 mb-2">💡 影响与行动</p>
              <ul className="text-sm text-slate-700 space-y-1">
                <li>• AI安全立场成为政府采购决定性因素</li>
                <li>• 创业机会：政府AI合规咨询、国防级AI安全工具</li>
                <li>• 风险：若Anthropic被封，国防承包商必须清除其技术</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Industry Feed */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">🌐</span>
            <h2 className="text-xl font-bold text-slate-800">行业动态 · Industry Feed</h2>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-lg transition">
              <span className="text-lg">🔥</span>
              <div className="flex-1">
                <p className="text-slate-800 font-medium">Anthropic遭五角大楼封杀威胁：因拒绝"任何合法使用"条款，可能被列为"供应链风险"</p>
                <p className="text-xs text-slate-500 mt-1">The Verge · 2小时前</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-lg transition">
              <span className="text-lg">💰</span>
              <div className="flex-1">
                <p className="text-slate-800 font-medium">OpenAI开启$1100亿融资：软银与NVIDIA各投$300亿，亚马逊投$500亿</p>
                <p className="text-xs text-slate-500 mt-1">CNBC · 4小时前</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-lg transition">
              <span className="text-lg">📱</span>
              <div className="flex-1">
                <p className="text-slate-800 font-medium">三星Galaxy S26发布：Gemini深度整合，AI预测用户行为并自动执行任务</p>
                <p className="text-xs text-slate-500 mt-1">Samsung · 6小时前</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-lg transition">
              <span className="text-lg">🤖</span>
              <div className="flex-1">
                <p className="text-slate-800 font-medium">阿里Qwen3.5：397B参数+201语言+原生多模态，瞄准AI Agent全球化</p>
                <p className="text-xs text-slate-500 mt-1">Alibaba · 8小时前</p>
              </div>
            </div>
          </div>
        </section>

        {/* Stock Radar */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">📈</span>
            <h2 className="text-xl font-bold text-slate-800">股票雷达 · Stock Radar</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-2 text-slate-600 font-medium">标的</th>
                  <th className="text-left py-2 text-slate-600 font-medium">代码</th>
                  <th className="text-left py-2 text-slate-600 font-medium">逻辑</th>
                  <th className="text-center py-2 text-slate-600 font-medium">趋势</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-100">
                  <td className="py-3 font-medium">科大讯飞</td>
                  <td className="py-3 text-slate-500">002230</td>
                  <td className="py-3 text-slate-700">国产AI替代逻辑</td>
                  <td className="py-3 text-center"><span className="text-green-600">📈</span></td>
                </tr>
                <tr className="border-b border-slate-100">
                  <td className="py-3 font-medium">寒武纪</td>
                  <td className="py-3 text-slate-500">688256</td>
                  <td className="py-3 text-slate-700">AI芯片国产替代</td>
                  <td className="py-3 text-center"><span className="text-green-600">📈</span></td>
                </tr>
                <tr className="border-b border-slate-100">
                  <td className="py-3 font-medium">Google</td>
                  <td className="py-3 text-slate-500">$GOOGL</td>
                  <td className="py-3 text-slate-700">接受五角大楼条款，国防订单受益</td>
                  <td className="py-3 text-center"><span className="text-green-600">📈</span></td>
                </tr>
                <tr>
                  <td className="py-3 font-medium">Palantir</td>
                  <td className="py-3 text-slate-500">$PLTR</td>
                  <td className="py-3 text-slate-700">依赖Claude的IL-6许可，风险大</td>
                  <td className="py-3 text-center"><span className="text-yellow-600">⚠️</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center py-8 border-t border-slate-200">
          <p className="text-sm text-slate-500">
            🤖 AGI决策情报 · 由小宇宙AI自动生成
          </p>
          <p className="text-xs text-slate-400 mt-2">
            每天早上8:00更新 · 信息源：50个（中文媒体/X博主/国际媒体）
          </p>
          <button className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium">
            💡 回复"深度"获取任意话题的详细分析
          </button>
        </footer>
      </main>
    </div>
  );
}
