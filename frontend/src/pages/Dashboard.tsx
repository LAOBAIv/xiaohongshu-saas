import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Button, Space, message, Modal, Form, Input, Switch, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SyncOutlined, ReloadOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useAuthStore } from '../stores/auth';
import { accountApi, statsApi } from '../api';
import { XHSAccount, StatsOverview, StatsTrend } from '../types';

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [trend, setTrend] = useState<StatsTrend | null>(null);
  const [accounts, setAccounts] = useState<XHSAccount[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchStats = async () => {
    try {
      const [statsRes, trendRes] = await Promise.all([
        statsApi.overview(),
        statsApi.trend('7d')
      ]);
      setStats(statsRes.data);
      setTrend(trendRes.data);
    } catch (error) {
      console.error('获取统计数据失败', error);
    }
  };

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const response = await accountApi.list({ page, page_size: 10 });
      setAccounts(response.data || []);
      setTotal(response.data?.length || 0);
    } catch (error) {
      message.error('获取账号列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchAccounts();
  }, [page]);

  const getTrendOption = () => ({
    tooltip: { trigger: 'axis' },
    legend: { data: ['回复数', '成功', '失败'] },
    xAxis: {
      type: 'category',
      data: trend?.data.map(d => d.date) || []
    },
    yAxis: { type: 'value' },
    series: [
      { name: '回复数', type: 'line', data: trend?.data.map(d => d.replies) || [] },
      { name: '成功', type: 'line', stack: 'total', data: trend?.data.map(d => d.success) || [] },
      { name: '失败', type: 'line', stack: 'total', data: trend?.data.map(d => d.failed) || [] }
    ]
  });

  const columns = [
    {
      title: '账号名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'login_status',
      key: 'login_status',
      render: (status: string) => {
        const color = status === 'valid' ? 'green' : status === 'invalid' ? 'red' : 'orange';
        const text = status === 'valid' ? '正常' : status === 'invalid' ? '失效' : '未知';
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: '监控评论',
      dataIndex: 'monitor_comments',
      key: 'monitor_comments',
      render: (val: boolean) => val ? <Tag color="blue">是</Tag> : <Tag>否</Tag>
    },
    {
      title: '监控私信',
      dataIndex: 'monitor_messages',
      key: 'monitor_messages',
      render: (val: boolean) => val ? <Tag color="blue">是</Tag> : <Tag>否</Tag>
    },
    {
      title: '最后检查',
      dataIndex: 'last_check_at',
      key: 'last_check_at',
      render: (val: string) => val ? new Date(val).toLocaleString() : '-'
    }
  ];

  return (
    <div>
      <h2>欢迎回来，{user?.nickname || user?.username} 👋</h2>
      
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="今日回复" value={stats?.today_replies || 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="总回复数" value={stats?.total_replies || 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="账号数量" value={stats?.total_accounts || 0} suffix={`/ ${stats?.active_accounts || 0} 活跃`} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="成功率" value={stats?.success_rate || 0} suffix="%" />
          </Card>
        </Col>
      </Row>

      {/* 趋势图表 */}
      <Card title="最近7天回复趋势" style={{ marginTop: 24 }}>
        {trend && <ReactECharts option={getTrendOption()} style={{ height: 300 }} />}
      </Card>

      {/* 账号列表 */}
      <Card 
        title="账号列表" 
        style={{ marginTop: 24 }}
        extra={<Button icon={<ReloadOutlined />} onClick={fetchAccounts}>刷新</Button>}
      >
        <Table 
          columns={columns} 
          dataSource={accounts} 
          rowKey="id" 
          loading={loading}
          pagination={{ current: page, pageSize: 10, total, onChange: setPage }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;