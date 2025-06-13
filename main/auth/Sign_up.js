const express = require('express');
const router = express.Router();
const supabase = require('../Supabase/Supabase'); // ← Supabaseの設定済みインスタンス

router.post('/signup', async (req, res) => {
  const { email, password, name } = req.body;

  try {
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({ email, password });
    if (signUpError) return res.status(400).json({ message: '認証エラー: ' + signUpError.message });

    const userId = signUpData?.user?.id;
    const { error: dbError } = await supabase.from('users').insert([{ email, name, user_id: userId }]);
    if (dbError) return res.status(400).json({ message: 'DBエラー: ' + dbError.message });

    res.status(200).json({ message: '登録完了しました！' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'サーバーエラーが発生しました' });
  }
});

module.exports = router;
