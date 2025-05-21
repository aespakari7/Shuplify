// Sign_up.js
const express = require('express');
const app = express();
const supabase = require('../Supabase/Supabase'); // ここでSupabaseを読み込む

app.use(express.json());

app.post('/signup', async (req, res) => {
  const { email, password, agent } = req.body;

  try {
    // Supabase認証
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
    });

    if (signUpError) throw signUpError;

    const userId = signUpData?.user?.id;

    // データベースにユーザー情報を追加
    const { error: dbError } = await supabase
      .from('users')
      .insert([{ email, agent, user_id: userId }]);

    if (dbError) throw dbError;

    res.status(200).json({ message: '登録完了しました！' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: '登録時にエラーが発生しました。' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`サーバー起動: http://localhost:${PORT}`));
