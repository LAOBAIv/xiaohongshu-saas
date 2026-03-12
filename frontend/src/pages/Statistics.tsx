import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Select, DatePicker, Button } from 'antd';
import ReactECharts from 'echarts-for-react';
import { statsApi, accountApi } from '../api';
import { StatsOverview, StatsTrend, ReplyHistoryItem, XHSAccount } from '../types';

const { RangePicker } = DatePicker;

const Statistics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [overview, setOverview] = useState<StatsOverview | null>(null);
  const [trend, setTrend] = useState<StatsTrend | null>(null);
  const [history, setHistory] = useState<ReplyHistoryItem[]>([]);
  const [accounts, setAccounts] = useState<XHSAccount[]>([]);
  const [period, setPeriod] = useState('7d');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({ account_id: undefined as number | undefined, target_type: undefined as string | undefined });

  const fetchOverview = async () => {
    try {
      const response = await statsApi.overview();
      setOverview(response.data);
    } catch (error) {
      console.error('获取概览失败', error);
    }
  };

  const fetchTrend = async () => {
    try {
      const response = await statsApi.trend(period);
      setTrend(response.data);
    } catch (error) {
      console.error('获取趋势失败', error);
    }
  };

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await statsApi.history({ page, page_size: 20, ...filters });
      setHistory(response.data?.items || []);
      setTotal(response.data?.total || 0);
    } catch (error) {
      console.error('获取历史失败', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await accountApi.list({ page_size: 100 });
      setAccounts(response.data || []);
    } catch (error) {
      console.error('获取账号失败', error);
    }
  };

  useEffect(() => {
    fetchOverview();
    fetchTrend();
    fetchHistory();
    fetchAccounts();
  }, []);

  useEffect(() => {
    fetchTrend();
  }, [period]);

  useEffect(() => {
    fetchHistory();
  }, [page, filters]);

  const getTrendOption = () => ({
    tooltip: { trigger: 'axis' },
    legend: { data: ['回复数', '成功', '失败'] },
    xAxis: { type: 'category', data: trend?.data.map(d => d.date) || [] },
    yAxis: { type: 'value' },
    series: [
      { name: '回复数', type: 'line', data: trend?.data.map(d => d.replies) || [] },
      { name: '成功', type: 'line', stack: 'total', data: trend?.data.map(d => d.success) || [], itemStyle: { color: '#52c41a' } },
      { name: '失败', type: 'line', stack: 'total', data: trend?.data.map(d => d.failed) || [], itemStyle: { color: '#ff4d4f' } }
    ]
  });

  const getPieOption = () => ({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: trend?.data.reduce((sum, d) => sum + d.success, 0) || 0, name: '成功' },
        { value: trend?.data.reduce((sum, d) => sum + d.failed, 0) || 0, name: '失败' }
      ]
    }]
  });

  const historyColumns = [
    { title: '时间', dataIndex: 'created_at', key: 'created_at', render: (v: string) => new Date(v).toLocaleString() },
    { title: '类型', dataIndex: 'target_type', key: 'target_type', render: (v: string) => <Tag color={v === 'comment' ? 'blue' : 'green'}>{v === 'comment' ? '评论' : '私信'}</Tag> },
    { title: '用户内容', dataIndex: 'target_content', key: 'target_content', ellipsis: true },
    { title: '回复内容', dataIndex: 'reply_content', key: 'reply_content', ellipsis: true },
    { title: '状态', dataIndex: 'reply_status', key: 'reply_status', render: (v: string) => <Tag color={v === 'success' ? 'green' : 'red'}>{v === 'success' ? '成功' : '失败'}</Tag> }
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}><Card><Statistic title="今日回复" value={overview?.today_replies || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="总回复数" value={overview?.total_replies || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="成功率" value={overview?.success_rate || 0} suffix="%" /></Card></Col>
        <Col span={6}><Card><Statistic title="活跃账号" value={overview?.active_accounts || 0} suffix={`/ ${overview?.total_accounts || 0}`} /></Card></Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card 
            title="回复趋势" 
            extra={
              <Select value={period} onChange={setPeriod} style={{ width: 120 }}>
                <Select.Option value="7d">最近7天</Select.Option>
                <Select.Option value="30d">最近30天</Select.Option>
                <Select.Option value="90d">最近90天</Select.Option>
              </Select>
            }
          >
            {trend && <ReactECharts option={getTrendOption()} style={{ height: 300 }} />}
          </Card>
        </Col>
        <Col span={8}>
          <Card title="成功率分布">
            {trend && <ReactECharts option={getPieOption()} style={{ height: 300 }} />}
          </Card>
        </Col>
      </Row>

      <Card title="回复历史">
        <div style={{ marginBottom: 16 }}>
          <Select 
            placeholder="筛选账号" 
            allowClear 
            style={{ width: 150, marginRight: 8 }}
            value={filters.account_id}
            onChange={(v) => setFilters(f => ({ ...f, account_id: v }))}
          >
            {accounts.map(a => <Select.Option key={a.id} value={a.id}>{a.name}</Select.Option>)}
          </Select>
          <Select 
            placeholder="筛选类型" 
            allowClear 
            style={{ width: 120, marginRight: 8 }}
            value={filters.target_type}
            onChange={(v) => setFilters(f => ({ ...f, target_type: v }))}
          >
            <Select.Option value="comment">评论</Select.Option>
            <Select.Option value="private_message">私信</Select.Option>
          </Select>
        </div>
        <Table 
          columns={historyColumns} 
          dataSource={history} 
          rowKey="id" 
          loading={loading}
          pagination={{ current: page, pageSize: 20, total, onChange: setPage }}
        />
      </Card>
    </div>
  );
};

export default Statistics;