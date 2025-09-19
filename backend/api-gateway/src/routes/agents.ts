import { Router } from 'express';

const router = Router();

router.get('/', (req, res) => {
  res.json({ message: 'Agents endpoint' });
});

export default router;
