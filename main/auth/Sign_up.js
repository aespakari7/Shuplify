const express = require('express');
const app = express();
const supabase = require('../Supabase/Supabase');

app.use(express.json());

app.post('/signup', async (req, res) => {
  const { email, password, name, agent } = req.body;

  try {
    // Supabase認証：ユーザー作成
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
    });

    if (signUpError) {
      return res.status(400).json({ message: '認証エラー: ' + signUpError.message });
    }

    const userId = signUpData?.user?.id;

    // usersテーブルに追加
    const { error: dbError } = await supabase
      .from('users')
      .insert([{ email, name, agent, user_id: userId }]);

    if (dbError) {
      return res.status(400).json({ message: 'DBエラー: ' + dbError.message });
    }

    res.status(200).json({ message: '登録完了しました！' });
  } catch (err) {
    console.error('例外エラー:', err);
    res.status(500).json({ message: 'サーバーエラーが発生しました。' });
  }
});