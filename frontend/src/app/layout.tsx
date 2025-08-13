export const metadata = {
  title: 'Deep Memory Research',
  description: 'Run deep research over your mem0 memory silo',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>{children}</body>
    </html>
  );
}


