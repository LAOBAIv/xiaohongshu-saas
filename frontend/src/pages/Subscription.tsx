import React from 'react';
import { Card, Row, Col, Button, Tag, List, Typography, Space, Badge } from 'antd';
import { CheckOutlined, CloseOutlined, CrownOutlined } from '@ant-design/icons';
import { useAuthStore } from '../stores/auth';

const { Title, Text } = Typography;

const Subscription: React.FC = () => {
  const { user } = useAuthStore();

  const plans = [
    {
      key: 'free',
      name: '免费版',
      price: 0,
      color: '#d9d9d9',
      features: [
        { text: '1个账号', available: true },
        { text: '每日50条回复', available: true },
        { text: '5条回复规则', available: true },
        { text: '评论监控', available: true },
        { text: '私信监控', available: false },
        { text: 'AI智能回复', available: false },
        { text: 'API接口', available: false },
        { text: '数据导出', available: false },
      ]
    },
    {
      key: 'pro',
      name: '专业版',
      price: 99,
      color: '#1890ff',
      popular: true,
      features: [
        { text: '5个账号', available: true },
        { text: '每日500条回复', available: true },
        { text: '50条回复规则', available: true },
        { text: '评论监控', available: true },
        { text: '私信监控', available: true },
        { text: 'AI智能回复', available: true },
        { text: 'API接口', available: true },
        { text: '数据导出', available: true },
      ]
    },
    {
      key: 'enterprise',
      name: '企业版',
      price: 299,
      color: '#faad14',
      features: [
        { text: '无限账号', available: true },
        { text: '无限回复', available: true },
        { text: '无限规则', available: true },
        { text: '评论监控', available: true },
        { text: '私信监控', available: true },
        { text: 'AI智能回复', available: true },
        { text: 'API接口', available: true },
        { text: '数据导出', available: true },
        { text: '专属客服', available: true },
      ]
    }
  ];

  const currentPlan = plans.find(p => p.key === user?.subscription_plan) || plans[0];

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Title level={2}>选择您的套餐</Title>
        <Text type="secondary">根据您的需求选择合适的套餐</Text>
      </div>

      <Row gutter={24} justify="center">
        {plans.map(plan => (
          <Col key={plan.key} span={8}>
            <Card 
              style={{ 
                borderColor: plan.key === user?.subscription_plan ? plan.color : undefined,
                position: 'relative'
              }}
              styles={{ body: { padding: 24 } }}
            >
              {plan.popular && (
                <Badge.Ribbon text="热门" color={plan.color} />
              )}
              {plan.key === user?.subscription_plan && (
                <Tag color={plan.color} style={{ position: 'absolute', top: 12, right: 12 }}>
                  当前套餐
                </Tag>
              )}
              
              <div style={{ textAlign: 'center', marginBottom: 24 }}>
                <CrownOutlined style={{ fontSize: 40, color: plan.color }} />
                <Title level={3} style={{ marginTop: 12 }}>{plan.name}</Title>
                <div style={{ fontSize: 32, fontWeight: 'bold', color: plan.color }}>
                  ¥{plan.price}
                  <Text type="secondary">/月</Text>
                </div>
              </div>

              <List
                dataSource={plan.features}
                renderItem={item => (
                  <List.Item>
                    <Space>
                      {item.available ? 
                        <CheckOutlined style={{ color: '#52c41a' }} /> : 
                        <CloseOutlined style={{ color: '#ff4d4f' }} />
                      }
                      <Text type={item.available ? 'default' : 'secondary'}>
                        {item.text}
                      </Text>
                    </Space>
                  </List.Item>
                )}
              />

              <Button 
                type={plan.key === user?.subscription_plan ? 'default' : 'primary'}
                block 
                disabled={plan.key === user?.subscription_plan}
                style={{ marginTop: 16 }}
              >
                {plan.key === user?.subscription_plan ? '当前套餐' : '立即订阅'}
              </Button>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default Subscription;